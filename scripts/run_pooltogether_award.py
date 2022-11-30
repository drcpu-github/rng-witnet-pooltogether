import json
import logging
import time

from brownie import config, Contract, RngWitnet, Wei

from dotenv import load_dotenv

from web3 import Web3

from util.helper_functions import get_events_alchemy
from util.helper_functions import setup_web3_provider

from util.network_functions import get_account
from util.network_functions import get_network

# This script is meant to run a full cycle of prize awarding

def start_award(network_config, transaction_parameters):
    assert len(network_config["prize_strategy_addresses"]) > 0, "At least one prize strategy address is required"

    prize_strategy_abi = json.loads(open("abis/multiple_winners_abi.json").read())

    # For each of the prize strategies, check if the award can be started and if so, complete it
    awards_started = set()
    for prize_strategy_address in network_config["prize_strategy_addresses"]:
        prize_strategy = Contract.from_abi("PrizeStrategy", prize_strategy_address, prize_strategy_abi)

        can_start = prize_strategy.canStartAward()

        if can_start:
            prize_strategy.startAward(transaction_parameters)

            logging.info(f"Started award for prize strategy at {prize_strategy_address}\n")
            awards_started.add(prize_strategy_address)
        else:
            logging.warning(f"Prize strategy {prize_strategy_address} is not ready for awarding\n")

    # Return prize strategies for which an award was started
    return awards_started

def fetch_random_numbers(network_config, w3_provider, transaction_parameters):
    # Grab an RngWitnet deployment
    assert network_config["rng_witnet_address"] != "", "An RngWitnet contract address is required"
    rng_witnet_abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
    rng_witnet = Contract.from_abi("RngWitnet", network_config["rng_witnet_address"], rng_witnet_abi)

    # Get events for which random numbers failed
    first_block_number = w3_provider.eth.get_transaction(network_config["rng_witnet_deploy_transaction"])["blockNumber"]
    last_block_number = w3_provider.eth.blockNumber
    rng_witnet_web3 = w3_provider.eth.contract(address=Web3.toChecksumAddress(network_config["rng_witnet_address"]), abi=rng_witnet_abi)

    random_numbers_failed = get_events_alchemy(rng_witnet_web3.events.RandomNumberFailed, first_block_number, last_block_number)
    failed_random_numbers = set([rng_failed["args"]["requestId"] for rng_failed in random_numbers_failed])

    logging.info(f"Random number requests which failed: {list(failed_random_numbers)}\n")

    # Get the total number of requests which have been made
    request_count = rng_witnet.requestCount()

    # Check which requests have not been fetched yet
    requests_to_fetch = []
    for request_id in range(1, request_count + 1):
        is_complete = rng_witnet.isRequestComplete(request_id)
        if not is_complete and request_id not in failed_random_numbers:
            requests_to_fetch.append(request_id)

    logging.info(f"Random number requests to fetch: {requests_to_fetch}\n")

    for request_id in requests_to_fetch:
        # Wait while the RNG request is being executed
        while True:
            is_request_fetchable = rng_witnet.isRngFetchable(request_id)
            logging.info(f"Is RNG request {request_id} fetchable: {is_request_fetchable}")
            if is_request_fetchable:
                break
            time.sleep(30)

        # Fetch the randomness into the contract
        txn = rng_witnet.fetchRandomness(
            request_id,
            transaction_parameters,
        )
        if "RandomNumberFailed" in txn.events:
            request_id = txn.events["RandomNumberFailed"][0][0]["requestId"]
            logging.error(f"Fetching the random number for request {request_id} failed\n")
        else:
            request_id = txn.events["RandomNumberCompleted"][0][0]["requestId"]
            random_number = txn.events["RandomNumberCompleted"][0][0]["randomNumber"]
            logging.info(f"Fetching the random number for request {request_id} succeeded: {random_number:x}\n")

def complete_award(awards_started, transaction_parameters):
    prize_strategy_abi = json.loads(open("abis/multiple_winners_abi.json").read())

    # For each of the prize strategies, check if the award can be completed and if so, complete it
    for prize_strategy_address in awards_started:
        prize_strategy = Contract.from_abi("PrizeStrategy", prize_strategy_address, prize_strategy_abi)

        can_complete = prize_strategy.canCompleteAward()

        if can_complete:
            prize_strategy.completeAward(transaction_parameters)
            logging.info(f"Completed award for prize strategy at {prize_strategy_address}\n")
        else:
            logging.warning(f"Cannot complete award for prize strategy at {prize_strategy_address}\n")

def main():
    print("")

    # Configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Add header formatting of the log message
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter("[%(levelname)-8s] [%(asctime)s] %(message)s", datefmt="%Y/%m/%d %H:%M:%S")

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    load_dotenv()

    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    w3_provider = setup_web3_provider(network, network_config["provider"])

    # Check if the current gas price does not exceed the configured maximum price
    current_gas_price = w3_provider.eth.gas_price
    if current_gas_price > Wei(network_config["max_gas_price"]):
        logging.warning(f"Refusing to start award since the gas price is {current_gas_price / 1E9:.3f} gwei\n")
        return

    # Set transaction parameters
    account = get_account()
    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    logging.info("Starting awards\n")
    # Hard code gas limit since the web3 estimation seems to be off
    transaction_parameters["gas_limit"] = 400000
    awards_started = start_award(network_config, transaction_parameters)

    logging.info("Fetch random numbers\n")
    # Remove hard coded gas limit
    del transaction_parameters["gas_limit"]
    fetch_random_numbers(network_config, w3_provider, transaction_parameters)

    logging.info("Completing awards\n")
    complete_award(awards_started, transaction_parameters)

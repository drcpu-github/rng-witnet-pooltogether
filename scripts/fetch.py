import json
import time

from brownie import accounts, config, Contract, RngWitnet

from dotenv import load_dotenv

from web3 import Web3

from util.helper_functions import get_events_alchemy
from util.helper_functions import setup_web3_provider

# This script is meant to check for and fetch outstanding random numbers.

def fetch(network):
    load_dotenv()

    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    w3_provider = setup_web3_provider(network, network_config["provider"])

    # Grab an RngWitnet deployment
    assert network_config["rng_witnet_address"] != "", "An RngWitnet contract address is required"
    abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
    rng_witnet = Contract.from_abi("RngWitnet", network_config["rng_witnet_address"], abi)

    # Get events for which random numbers failed
    first_block_number = w3_provider.eth.get_transaction(network_config["rng_witnet_deploy_transaction"])["blockNumber"]
    last_block_number = w3_provider.eth.blockNumber
    rng_witnet_web3 = w3_provider.eth.contract(address=Web3.toChecksumAddress(network_config["rng_witnet_address"]), abi=abi)

    random_numbers_failed = get_events_alchemy(rng_witnet_web3.events.RandomNumberFailed, first_block_number, last_block_number)
    failed_random_numbers = set([rng_failed["args"]["requestId"] for rng_failed in random_numbers_failed])

    print(f"Random number requests which failed: {failed_random_numbers}")

    # Get the total number of requests which have been made
    request_count = rng_witnet.requestCount()

    # Check which requests have not been fetched yet
    requests_to_fetch = []
    for request_id in range(1, request_count + 1):
        is_complete = rng_witnet.isRequestComplete(request_id)
        if not is_complete and request_id not in failed_random_numbers:
            requests_to_fetch.append(request_id)

    print(f"Random number requests to fetch: {requests_to_fetch}")

    account = get_account()
    for request_id in requests_to_fetch:
        # Wait while the RNG request is being executed
        while True:
            is_request_fetchable = rng_witnet.isRngFetchable(request_id)
            print(f"Is RNG request {request_id} fetchable: {is_request_fetchable}")
            if is_request_fetchable:
                break
            time.sleep(30)

        # Fetch the randomness into the contract
        txn = rng_witnet.fetchRandomness(
            request_id,
            {
                "from": account,
                "priority_fee": network_config["priority_fee"],
                "max_fee": network_config["max_fee"],
            }
        )
        if "RandomNumberFailed" in txn.events:
            request_id = txn.events["RandomNumberFailed"][0][0]["requestId"]
            print(f"Fetching the random number for request {request_id} failed")
        else:
            request_id = txn.events["RandomNumberCompleted"][0][0]["requestId"]
            random_number = txn.events["RandomNumberCompleted"][0][0]["randomNumber"]
            print(f"Fetching the random number for request {request_id} succeeded: {random_number:x}")

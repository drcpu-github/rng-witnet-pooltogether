import json
import time

from brownie import accounts, config, Contract, RngWitnet

from util.network_functions import get_account
from util.network_functions import get_network

# This script serves as an example for the steps required to fetch a random number.
# It only works if you add yourself as an allowed requester to the contract.

def main():
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    # Grab an RngWitnet deployment
    assert network_config["rng_witnet_address"] != "", "An RngWitnet contract address is required"
    abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
    rng_witnet = Contract.from_abi("RngWitnet", network_config["rng_witnet_address"], abi)

    # Request random number
    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]
    transaction_parameters["gas_limit"] = 300000

    txn = rng_witnet.requestRandomNumber(
        transaction_parameters,
    )
    contract_request_id = txn.events["RngRequested"]["requestId"]
    witnet_request_id = txn.events["RngRequested"]["witnetRequestId"]
    print(f"Randomness request {contract_request_id} => {witnet_request_id}")

    # Wait while the RNG request is being executed
    while True:
        is_request_fetchable = rng_witnet.isRngFetchable(contract_request_id)
        print(f"Is RNG request {contract_request_id} fetchable: {is_request_fetchable}")
        if is_request_fetchable:
            break
        time.sleep(30)

    # Fetch the randomness into the contract
    del transaction_parameters["gas_limit"]
    rng_witnet.fetchRandomness(
        contract_request_id,
        transaction_parameters,
    )

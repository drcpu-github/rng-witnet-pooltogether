import json
import time

from brownie import accounts, config, Contract, RngWitnet

# This script is meant to check whether there are any outstanding and fetchable random numbers.

def main():
    script_config = json.load(open("config.json"))

    # Use the account defined in .env
    accounts.add(config["wallets"]["from_key"])
    my_account = accounts[0]

    # Grab an RngWitnet deployment
    if script_config["rng_witnet_address"] != "":
        abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
        rng_witnet = Contract.from_abi("RngWitnet", script_config["rng_witnet_address"], abi)
    else:
        rng_witnet = RngWitnet[-1]

    # Get the total number of requests which have been made
    request_count = rng_witnet.requestCount()

    # Check which requests have not been fetched yet
    requests_to_fetch = []
    for request_id in range(1, request_count + 1):
        is_complete = rng_witnet.isRequestComplete(request_id)
        if not is_complete:
            requests_to_fetch.append(request_id)

    for request_id in requests_to_fetch:
        # Wait while the RNG request is being executed
        while True:
            is_request_fetchable = rng_witnet.isRngFetchable(request_id)
            print(f"Is RNG request {request_id} fetchable: {is_request_fetchable}")
            if is_request_fetchable:
                break
            time.sleep(30)

        # Fetch the randomness into the contract
        txn = rng_witnet.fetchRandomness(request_id, {"from": my_account})
        if "RandomNumberFailed" in txn.events:
            request_id = txn.events["RandomNumberFailed"][0][0]["requestId"]
            print(f"Fetching the random number for request {request_id} failed")
        else:
            request_id = txn.events["RandomNumberCompleted"][0][0]["requestId"]
            random_number = txn.events["RandomNumberCompleted"][0][0]["randomNumber"]
            print(f"Fetching the random number for request {request_id} succeeded: {random_number:x}")

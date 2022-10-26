import json
import time

from brownie import accounts, config, Contract, RngWitnet

# This script serves as an example for the steps required to fetch a random number.
# It only works if you add yourself as an allowed requester to the contract.

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

    # Request random number
    txn = rng_witnet.requestRandomNumber({"from": my_account, "gas_limit": 300000})
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
    rng_witnet.fetchRandomness(contract_request_id, {"from": my_account})

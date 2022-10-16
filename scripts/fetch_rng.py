import time

from brownie import accounts, config, RngWitnet

# This scripts works as an example.
# It only works if you add yourself as an allowed requester to the contract.

def main():
    # Use the account defined in .env
    accounts.add(config["wallets"]["from_key"])
    my_account = accounts[0]

    # Grab the latest deployment
    rng_witnet = RngWitnet[-1]

    # Request random number
    txn = rng_witnet.requestRandomNumber({"from": my_account, "gas_limit": 400000})
    contract_request_id = txn.events["RngRequested"]["requestId"]
    witnet_request_id = txn.events["RngRequested"]["witnetRequestId"]
    print(f"Randomness request {contract_request_id} => {witnet_request_id}")

    # Wait while the RNG request is being executed
    while True:
        is_request_complete = rng_witnet.isRequestComplete(contract_request_id)
        print(f"Is RNG request {contract_request_id} complete: {is_request_complete}")
        if is_request_complete:
            break
        time.sleep(30)

    # Fetch the randomness into the contract
    rng_witnet.fetchRandomness(contract_request_id, {"from": my_account})

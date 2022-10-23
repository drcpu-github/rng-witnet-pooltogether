import json

from brownie import accounts, config, Contract, RngWitnet, Wei

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

    rng_witnet.setMaxFee(Wei(script_config["max_fee"]), {"from": my_account})

import json

from brownie import accounts, config, Contract, RngWitnet

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

    # Print owner of Witnet randomness request instantation
    abi = json.loads(open("build/contracts/WitnetRequestRandomness.json").read())["abi"]
    witnet_randomness_request = Contract.from_abi("WitnetRequestRandomness", rng_witnet.witnetRandomnessRequest(), abi)
    print(witnet_randomness_request.owner())

    # Set witnessing parameters
    witnet_randomness_request.setWitnessingParameters(10 ** 10, 10 ** 8, 10 ** 6, 8, 51, {"from": my_account})

import json

from brownie import accounts, config, Contract, RngWitnet

from util.network_functions import get_account
from util.network_functions import get_network

def main():
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    # Grab an RngWitnet deployment
    assert network_config["rng_witnet_address"] != "", "An RngWitnet contract address is required"
    abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
    rng_witnet = Contract.from_abi("RngWitnet", network_config["rng_witnet_address"], abi)

    print(f"RngWitnet deployment: {rng_witnet}")

    # Print owner of Witnet randomness request instantation
    abi = json.loads(open("build/contracts/WitnetRequestRandomness.json").read())["abi"]
    witnet_randomness_request = Contract.from_abi("WitnetRequestRandomness", rng_witnet.witnetRandomnessRequest(), abi)
    print(f"Owner of the Witnet Randomness Request: {witnet_randomness_request.owner()}")

    # Set witnessing parameters
    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    witnet_randomness_request.setWitnessingParameters(
        10 ** 10,   # collateral
        10 ** 8,    # witness reward
        10 ** 6,    # commit and reveal inclusion fees
        8,          # witnesses
        51,         # consensus percentage
        transaction_parameters,
    )

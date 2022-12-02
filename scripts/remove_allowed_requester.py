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

    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    for address in network_config["remove_requesters"]:
        rng_witnet.removeAllowedRequester(
            address,
            transaction_parameters,
        )

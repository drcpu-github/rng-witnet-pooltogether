import json

from brownie import accounts, config, Contract, RngWitnet, Wei

from util.network_functions import get_account
from util.network_functions import get_network

def main(network):
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    # Grab an RngWitnet deployment
    assert network_config["rng_witnet_address"] != "", "An RngWitnet contract address is required"
    abi = json.loads(open("build/contracts/RngWitnet.json").read())["abi"]
    rng_witnet = Contract.from_abi("RngWitnet", network_config["rng_witnet_address"], abi)

    account = get_account(0)
    rng_witnet.setMaxFee(Wei(network_config["max_fee"]), {"from": my_account})

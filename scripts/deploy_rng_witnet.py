import json

from brownie import RngWitnet

from util.network_functions import get_account
from util.network_functions import get_network
from util.network_functions import is_local_network

def main():
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"

    network_config = script_config[network]

    assert network_config["witnet_request_board_address"] != "", "Need to specify the address of the Witnet Request Board"
    assert network_config["witnet_request_randomness_address"] != "", "Need to specify the address of the Witnet Request Randomness"

    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    return RngWitnet.deploy(
        network_config["witnet_request_board_address"],
        network_config["witnet_request_randomness_address"],
        transaction_parameters,
        publish_source=not is_local_network(),
    )

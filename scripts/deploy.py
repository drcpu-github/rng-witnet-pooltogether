import json

from brownie import accounts, config, RngWitnet, WitnetRequestRandomness

from util.network_functions import get_account
from util.network_functions import get_network
from util.network_functions import is_local_network

def deploy_rng_witnet():
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"
    network_config = script_config[network]

    assert network_config["witnet_request_board_address"] != "", "Need to specify the address of the Witnet Request Board"
    assert network_config["witnet_request_randomness_address"] != "", "Need to specify the address of the Witnet Request Randomness"

    account = get_account(0)

    RngWitnet.deploy(
        network_config["witnet_request_board_address"],
        network_config["witnet_request_randomness_address"],
        {"from": account},
        publish_source=not is_local_network()
    )

def deploy_witnet_request_randomness():
    account = get_account(0)
    WitnetRequestRandomness.deploy({"from": account}, publish_source=not is_local_network())

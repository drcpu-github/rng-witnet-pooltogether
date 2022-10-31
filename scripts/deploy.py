import json

from brownie import accounts, config, RngWitnet, WitnetRequestRandomness

from util.network_functions import get_account
from util.network_functions import get_network
from util.network_functions import is_local_network

def get_network_config():
    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"

    return script_config[network]

def deploy_rng_witnet():
    network_config = get_network_config()

    assert network_config["witnet_request_board_address"] != "", "Need to specify the address of the Witnet Request Board"
    assert network_config["witnet_request_randomness_address"] != "", "Need to specify the address of the Witnet Request Randomness"

    account = get_account()

    RngWitnet.deploy(
        network_config["witnet_request_board_address"],
        network_config["witnet_request_randomness_address"],
        {
            "from": account,
            "priority_fee": network_config["priority_fee"],
            "max_fee": network_config["max_fee"],
        },
        publish_source=not is_local_network(),
    )

def deploy_witnet_request_randomness():
    network_config = get_network_config()

    account = get_account()

    WitnetRequestRandomness.deploy(
        {
            "from": account,
            "priority_fee": network_config["priority_fee"],
            "max_fee": network_config["max_fee"],
        },
        publish_source=not is_local_network(),
    )

import json

from brownie import accounts, config, RngWitnet, WitnetRequestRandomness

def deploy_rng_witnet_goerli():
    deploy_rng_witnet("goerli")

def deploy_rng_witnet(network):
    script_config = json.load(open("config.json"))

    accounts.add(config["wallets"]["from_key"])
    deploy_account = accounts[0]

    assert network in script_config, "Network configuration not found"
    assert script_config[network]["witnet_request_board_address"] != "", "Need to specify the address of the Witnet Request Board"
    assert script_config[network]["witnet_request_randomness_address"] != "", "Need to specify the address of the Witnet Request Randomness"

    RngWitnet.deploy(
        script_config[network]["witnet_request_board_address"],
        script_config[network]["witnet_request_randomness_address"],
        {"from": deploy_account},
        publish_source=True
    )

def deploy_witnet_request_randomness():
    accounts.add(config["wallets"]["from_key"])
    deploy_account = accounts[0]

    WitnetRequestRandomness.deploy({"from": deploy_account}, publish_source=True)

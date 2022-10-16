import json

from brownie import accounts, config, RngWitnet

def deploy_goerli():
    deploy("goerli")

def deploy(network):
    script_config = json.load(open("config.json"))

    accounts.add(config["wallets"]["from_key"])
    deploy_account = accounts[0]

    RngWitnet.deploy(script_config[network]["witnet_request_board_address"], {"from": deploy_account}, publish_source=True)

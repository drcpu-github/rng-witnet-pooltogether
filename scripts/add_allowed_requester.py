import json

from brownie import accounts, config, Contract, RngWitnet

def add_requesters_goerli():
    add_requesters("goerli")

def add_requesters(network):
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

    for address in script_config[network]["prize_strategy_addresses"]:
        rng_witnet.addAllowedRequester(address, {"from": my_account})

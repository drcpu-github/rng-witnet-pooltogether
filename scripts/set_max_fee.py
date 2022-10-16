import json

from brownie import accounts, config, RngWitnet, Wei

def main():
    script_config = json.load(open("config.json"))

    # Use the account defined in .env
    accounts.add(config["wallets"]["from_key"])
    my_account = accounts[0]

    # Grab the latest deployment
    rng_witnet = RngWitnet[-1]

    rng_witnet.setMaxFee(Wei(script_config["max_fee"]), {"from": my_account})

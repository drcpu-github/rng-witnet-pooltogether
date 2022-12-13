import json
import logging
import time

from brownie import WitnetRequestRandomness

from util.logger import setup_stdout_logger

from util.network_functions import get_account
from util.network_functions import get_network
from util.network_functions import is_local_network

def main():
    setup_stdout_logger()

    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"

    network_config = script_config[network]

    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    return WitnetRequestRandomness.deploy(
        transaction_parameters,
        publish_source=not is_local_network(),
    )

    while True:
        try:
            return WitnetRequestRandomness.deploy(
                transaction_parameters,
                publish_source=not is_local_network(),
            )
        except ValueError as e:
            if e.args[0] in ("transaction underpriced", "replacement transaction underpriced"):
                logging.warning("Transaction underpriced, retrying in 60 seconds")
                time.sleep(60)
                continue
            raise

import json
import logging
import time

from brownie import RngWitnet, RngWitnetMock

from util.logger import setup_stdout_logger

from util.network_functions import get_account
from util.network_functions import get_network
from util.network_functions import is_local_network
from util.network_functions import is_testnet

def main(_witnet_request_randomness_address="", _mockGas=0, _mockReward=0):
    setup_stdout_logger()

    if is_testnet():
        assert _witnet_request_randomness_address == "", "On a testnet, _witnet_request_randomness_address should not be initialized"
        assert _mockGas == 0, "On a testnet, _mockGas should not be initialized"
        assert _mockReward == 0, "On a testnet, _mockReward should not be initialized"

    network = get_network()

    script_config = json.load(open("config.json"))
    assert network in script_config, "Network configuration not found"

    network_config = script_config[network]

    assert network_config["witnet_request_board_address"] != "", "Need to specify the address of the Witnet Request Board"

    witnet_request_randomness_address = ""
    if "witnet_request_randomness_address" in network_config and network_config["witnet_request_randomness_address"] != "":
        witnet_request_randomness_address = network_config["witnet_request_randomness_address"]
    else:
        witnet_request_randomness_address = _witnet_request_randomness_address
    assert witnet_request_randomness_address != "", "Need to specify the address of the Witnet Request Randomness"

    account = get_account()

    transaction_parameters = {"from": account}
    if network_config["priority_fee"] != "" and network_config["max_fee"] != "":
        transaction_parameters["priority_fee"] = network_config["priority_fee"]
        transaction_parameters["max_fee"] = network_config["max_fee"]

    if is_local_network():
        return RngWitnetMock.deploy(
            network_config["witnet_request_board_address"],
            witnet_request_randomness_address,
            _mockGas,
            _mockReward,
            transaction_parameters,
        )
    else:
        while True:
            try:
                return RngWitnet.deploy(
                    network_config["witnet_request_board_address"],
                    witnet_request_randomness_address,
                    transaction_parameters,
                    publish_source=True,
                )
            except ValueError as e:
                if e.args[0] in ("transaction underpriced", "replacement transaction underpriced"):
                    logging.warning("Transaction underpriced, retrying in 60 seconds")
                    time.sleep(60)
                    continue
                raise

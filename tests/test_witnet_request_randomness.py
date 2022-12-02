import brownie
import pytest

from brownie import accounts, Wei, WitnetRequestRandomness

from web3 import Web3

from scripts.deploy_witnet_request_randomness import main as deploy_witnet_request_randomness

from util.constants import requestAlreadyInitialized
from util.constants import noWitnessingReward
from util.constants import invalidNumWitnesses
from util.constants import invalidWitnessingConsensus
from util.constants import invalidWitnessingCollateral

from util.network_functions import get_account

@pytest.fixture
def witnet_request_randomness():
    return deploy_witnet_request_randomness()

@pytest.fixture
def configured_witnet_request_randomness(witnet_request_randomness):
    account = get_account()

    witnet_request_randomness.setWitnessingParameters(
        1E9,
        1E6,
        1E3,
        8,
        75,
        {"from": account},
    )

    return witnet_request_randomness

# Test setting the witness reward to an (in)valid value
def test_witnessing_reward(witnet_request_randomness):
    account = get_account()

    # This transaction should revert, we cannot call setWitnessingMonetaryPolicy with a zero reward
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the noWitnessingReward error
    expected_error = f"typed error: {noWitnessingReward}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingMonetaryPolicy(
            1E9,
            0,
            1E3,
            {"from": account},
        )

    witnet_request_randomness.setWitnessingMonetaryPolicy(
        1E9,
        1E6,
        1E3,
        {"from": account},
    )

# Test setting the amount of witnesses to an (in)valid value
def test_num_witnesses(witnet_request_randomness):
    account = get_account()

    # This transaction should revert, we cannot call setWitnessingMonetaryPolicy with a zero reward
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the invalidNumWitnesses error
    #   2) An zero-prefixed 64 bytes hexadecimal string detailing how many witnesses were attempted to be set
    witnesses_str = f"{130:064x}"
    expected_error = f"typed error: {invalidNumWitnesses}{witnesses_str}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingQuorum(
            130,
            90,
            {"from": account},
        )

    witnesses_str = f"{0:064x}"
    expected_error = f"typed error: {invalidNumWitnesses}{witnesses_str}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingQuorum(
            0,
            90,
            {"from": account},
        )

    witnet_request_randomness.setWitnessingQuorum(
        8,
        90,
        {"from": account},
    )

# Test setting the witnessing consensus to an (in)valid value
def test_witnessing_consensus(witnet_request_randomness):
    account = get_account()

    # This transaction should revert, we cannot call setWitnessingQuorum with a consensus value below 51 or above 99
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the invalidNumWitnesses error
    #   2) An zero-prefixed 64 bytes hexadecimal string detailing which consensus percentage was attempted to be set
    consensus_str = f"{50:064x}"
    expected_error = f"typed error: {invalidWitnessingConsensus}{consensus_str}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingQuorum(
            8,
            50,
            {"from": account},
        )

    consensus_str = f"{100:064x}"
    expected_error = f"typed error: {invalidWitnessingConsensus}{consensus_str}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingQuorum(
            8,
            100,
            {"from": account},
        )

    witnet_request_randomness.setWitnessingQuorum(
        8,
        75,
        {"from": account},
    )

# Test setting the witnessing collateral to an (in)valid value
def test_witnessing_collateral(witnet_request_randomness):
    account = get_account()

    # This transaction should revert, we cannot call setWitnessingMonetaryPolicy with a zero reward
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the noWitnessingReward error
    #   2) A zero-prefixed 64 bytes hexadecimal string detailing which witnessing collateral which was attempted to be set
    collateral_str = f"{int(1E8):064x}"
    expected_error = f"typed error: {invalidWitnessingCollateral}{collateral_str}"
    with brownie.reverts(expected_error):
        witnet_request_randomness.setWitnessingMonetaryPolicy(
            1E8,
            1E6,
            1E3,
            {"from": account},
        )

    witnet_request_randomness.setWitnessingMonetaryPolicy(
        1E9,
        1E6,
        1E3,
        {"from": account},
    )

# Test if the total collateral is calculated correctly
def test_total_witnessing_collateral(configured_witnet_request_randomness):
    collateral, num_witnesses = 1E9, 8
    assert configured_witnet_request_randomness.totalWitnessingCollateral() == int(collateral * num_witnesses)

# Test if the total fee is calculated correctly
def test_total_witnessing_fee(configured_witnet_request_randomness):
    num_witnesses = 8
    miner_fee = 1E3
    witness_reward = 1E6
    assert configured_witnet_request_randomness.totalWitnessingFee() == int(num_witnesses * (2 * miner_fee + witness_reward))

# Test fetching and setting new witnessing parameters
def test_witnessing_params(configured_witnet_request_randomness):
    account = get_account()

    # Fetch the new parameters
    numWitnesses, minWitnessingConsensus, witnessingCollateral, witnessingReward, witnessingUnitaryFee = configured_witnet_request_randomness.witnessingParams()

    assert numWitnesses == 8
    assert minWitnessingConsensus == 75
    assert witnessingCollateral == 1E9
    assert witnessingReward == 1E6
    assert witnessingUnitaryFee == 1E3

    # Set new parameters
    configured_witnet_request_randomness.setWitnessingParameters(
        1E10,
        1E7,
        1E4,
        16,
        90,
        {"from": account},
    )

    # Fetch the new parameters
    numWitnesses, minWitnessingConsensus, witnessingCollateral, witnessingReward, witnessingUnitaryFee = configured_witnet_request_randomness.witnessingParams()

    assert numWitnesses == 16
    assert minWitnessingConsensus == 90
    assert witnessingCollateral == 1E10
    assert witnessingReward == 1E7
    assert witnessingUnitaryFee == 1E4

# Test transfering the ownership of the Witnet Randomness Request
def test_transfer_ownership(witnet_request_randomness):
    account = get_account(index=0)
    deployer_account = f"{account}"

    # Check if the request is owned by the deployer
    assert witnet_request_randomness.owner() == deployer_account

    account = get_account(index=1)

    # Transfer to a new owner
    witnet_request_randomness.transferOwnership(account)

    # Check if it is owned by the new owner
    assert witnet_request_randomness.owner() != f"{deployer_account}"
    assert witnet_request_randomness.owner() == f"{account}"

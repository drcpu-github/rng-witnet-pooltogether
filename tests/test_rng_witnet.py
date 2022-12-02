import brownie
import pytest

from brownie import RngWitnet, Wei, WitnetRequestRandomness
from brownie.network.state import Chain

from scripts.deploy_rng_witnet import main as deploy_rng_witnet
from scripts.deploy_witnet_request_randomness import main as deploy_witnet_request_randomness

from util.constants import disallowedRequester
from util.constants import maxFeeTooLow
from util.constants import balanceTooLow
from util.constants import randomnessNotAvailable

from util.network_functions import get_account

@pytest.fixture
def witnet_request_randomness():
    return deploy_witnet_request_randomness()

@pytest.fixture
def rng_witnet(witnet_request_randomness):
    return deploy_rng_witnet(
        _witnet_request_randomness_address=witnet_request_randomness,
        _mockGas=1E8,
        _mockReward=1E9,
    )

@pytest.fixture
def rng_witnet_with_balance(rng_witnet):
    account = get_account()

    # Transfer some Ether to the RngWitnet contract
    account.transfer(rng_witnet, "1 ether")

    # Return the initialized contract
    return rng_witnet

@pytest.fixture
def rng_witnet_with_requester(rng_witnet_with_balance):
    account = get_account()

    # Set the given address as an allowed requester
    rng_witnet_with_balance.addAllowedRequester(
        account,
        {"from": account},
    )

    return rng_witnet_with_balance

# Test refunding the contract balance to the original account
def test_refund(rng_witnet_with_balance):
    account = get_account()

    assert account.balance() == Wei("999 ether")

    rng_witnet_with_balance.refund()

    assert account.balance() == Wei("1000 ether")

# Check that the randomness request can be updated to a new one
def test_set_witnet_request_randomness(rng_witnet):
    current_randomness_request = rng_witnet.witnetRandomnessRequest()

    rng_witnet.setWitnetRequestRandomness(current_randomness_request)

    assert current_randomness_request != rng_witnet.witnetRandomnessRequest()

# Check that requestRandomNumber reverts when the maximum fee is too low
def test_max_fee_too_low(rng_witnet_with_requester):
    account = get_account()

    # This transaction should revert, we cannot call requestRandomNumber from 'account'
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the disallowedRequester error
    #   2) A zero-prefixed 64 bytes hexadecimal string for the current maximum fee
    #   3) A zero-prefixed 64 bytes hexadecimal string for the required fee to pay for the reward
    reward = f"{int(1E9):064x}"
    expected_error = f"typed error: {maxFeeTooLow}{'0'.zfill(64)}{reward.zfill(64)}"
    with brownie.reverts(expected_error):
        rng_witnet_with_requester.requestRandomNumber(
            {"from": account}
        )

# Test setting the maximum RNG fee
def test_set_max_fee(rng_witnet):
    account = get_account()

    rng_witnet.setMaxFee(
        Wei("0.01 ether"),
        {"from": account},
    )

    assert rng_witnet.maxFee() == Wei("0.01 ether")

# Test getting the current (mock) request fee
# getRequestFee() does not work under ganache-cli because it does not support the london hardfork
def test_get_request_fee(rng_witnet):
    request_fee = rng_witnet.getRequestFee(10)

    assert request_fee == 1E9

# Check that requestRandomNumber reverts when the contract's balance is too low
def test_balance_too_low(rng_witnet):
    account = get_account()

    # Set the given address as an allowed requester
    rng_witnet.addAllowedRequester(
        account,
        {"from": account},
    )

    # Set max fee
    test_set_max_fee(rng_witnet)

    # This transaction should revert, we cannot call requestRandomNumber if the balance of the contract is too low
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the balanceTooLow error
    #   2) A zero-prefixed 64 bytes hexadecimal string for the current balance
    #   3) A zero-prefixed 64 bytes hexadecimal string for the required balance
    reward = f"{int(1E9):064x}"
    expected_error = f"typed error: {balanceTooLow}{'0'.zfill(64)}{reward.zfill(64)}"
    with brownie.reverts(expected_error):
        rng_witnet.requestRandomNumber(
            {"from": account}
        )

# Check that we can request a random number
def test_request_random_numbers(rng_witnet_with_requester):
    account = get_account(index=0)

    # Set the maximum fee
    test_set_max_fee(rng_witnet_with_requester)

    # Requesting a random number with an allowed requester should result in a succesful call
    rng_witnet_with_requester.requestRandomNumber(
        {"from": account}
    )

    # Get last request ID should return 1
    assert rng_witnet_with_requester.getLastRequestId() == 1

    account = get_account(index=1)

    # This transaction should revert, we cannot call requestRandomNumber from 'account'
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the disallowedRequester error
    #   2) A zero-prefixed 64 bytes hexadecimal string for the address 'account'
    account_str = f"{account}"[2:].lower()
    expected_error = f"typed error: {disallowedRequester}{account_str.zfill(64)}"
    with brownie.reverts(expected_error):
        rng_witnet_with_requester.requestRandomNumber(
            {"from": account}
        )

    account = get_account(index=0)

    # Requesting a random number with an allowed requester should result in a succesful call
    rng_witnet_with_requester.requestRandomNumber(
        {"from": account}
    )

    # Get last request ID should return 2
    assert rng_witnet_with_requester.getLastRequestId() == 2

# Check that we can remove an allowed requester by running a requestRandomNumber
def test_remove_allowed_requester(rng_witnet_with_requester):
    account = get_account()

    # First remove the previously added requester
    rng_witnet_with_requester.removeAllowedRequester(
        account,
        {"from": account},
    )

    # This transaction should revert, we cannot call requestRandomNumber from 'account' anymore
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the disallowedRequester error
    #   2) A zero-prefixed 64 bytes hexadecimal string for the address 'account'
    account_str = f"{account}"[2:].lower()
    expected_error = f"typed error: {disallowedRequester}{account_str.zfill(64)}"
    with brownie.reverts(expected_error):
        rng_witnet_with_requester.requestRandomNumber(
            {"from": account}
        )

# Check that we can request a random number
def test_is_rng_fetchable(rng_witnet_with_requester):
    chain = Chain()

    account = get_account()

    # Set the maximum fee
    test_set_max_fee(rng_witnet_with_requester)

    # Requesting a random number with an allowed requester should result in a succesful call
    request = rng_witnet_with_requester.requestRandomNumber(
        {"from": account}
    )
    (requestId, lockBlock) = request.return_value

    # The RNG is not yet available immediately after requesting it
    assert rng_witnet_with_requester.isRngFetchable(requestId) == False

    block_number = chain.mine(10)

    # The RNG is available after waiting 10 blocks
    assert rng_witnet_with_requester.isRngFetchable(requestId) == True

def test_is_request_complete(rng_witnet_with_requester):
    chain = Chain()

    account = get_account()

    # Set the maximum fee
    test_set_max_fee(rng_witnet_with_requester)

    # Requesting a random number with an allowed requester should result in a succesful call
    request = rng_witnet_with_requester.requestRandomNumber(
        {"from": account}
    )
    (requestId, lockBlock) = request.return_value

    # The request cannot be complete immediately after requesting it
    assert rng_witnet_with_requester.isRequestComplete(requestId) == False

    # This transaction should revert, we cannot call fetchRandomness before it is available
    # The revert error should have the following format:
    #   1) An 8 byte hexadecimal string representing the disallowedRequester error
    #   2) A zero-prefixed 64 bytes hexadecimal string for the address 'account'
    request_id_str = f"{requestId}"
    expected_error = f"typed error: {randomnessNotAvailable}{request_id_str.zfill(64)}"
    with brownie.reverts(expected_error):
        rng_witnet_with_requester.fetchRandomness(
            requestId,
            {"from": account},
        )

    block_number = chain.mine(10)

    # The request is not complete until it has been fetched
    assert rng_witnet_with_requester.isRequestComplete(requestId) == False

    # Fetch randomness
    rng_witnet_with_requester.fetchRandomness(
        requestId,
        {"from": account},
    )

    # The request has now been completed
    assert rng_witnet_with_requester.isRequestComplete(requestId) == True

    # The true random number is always 9: https://dilbert.com/strip/2001-10-25
    assert rng_witnet_with_requester.randomNumber(requestId) == 9

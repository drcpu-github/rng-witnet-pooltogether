// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.6;

import "@openzeppelin/contracts/access/Ownable.sol";

import "@pooltogether/pooltogether-rng-contracts/contracts/RNGInterface.sol";

import "@witnet/witnet-solidity-bridge/contracts/UsingWitnet.sol";
import "@witnet/witnet-solidity-bridge/contracts/requests/WitnetRequest.sol";

contract RngWitnet is RNGInterface, UsingWitnet, Ownable {
    event MaxFeeSet(uint256 maxFee);
    event RandomNumberFailed(uint32 requestId);
    event Received(address, uint);
    event RequestSet(bytes request);
    event RequesterAdded(address requester);
    event RngRequested(uint32 indexed requestId, uint256 witnetRequestId);
    event WrbSet(WitnetRequestBoard witnetRequestBoard);

    /// @dev Low-level Witnet Data Request composed on construction
    IWitnetRequest public witnetRequest;

    /// @dev The maximum request fee for the Witnet RNG
    uint256 public maxFee;

    /// @dev A counter for the number of requests made used for request ids
    uint32 public requestCount;

    /// @dev The addresses which are allowed to request random numbers
    mapping(address => bool) allowedRequester;

    /// @dev A list of random numbers from past requests mapped by request id
    mapping(uint32 => uint256) internal randomNumbers;

    /// @dev A list of bools to check whether the random number has been fetched
    mapping(uint32 => bool) internal randomNumberFetched;

    /// @dev A list of blocks to be locked at based on past requests mapped by request id
    mapping(uint32 => uint32) internal requestLockBlock;

    /// @dev A mapping from internal request ids to Witnet Request ids
    mapping(uint32 => uint256) internal witnetRequestIds;

    /// @dev Public constructor
    constructor(WitnetRequestBoard _witnetRequestBoard) UsingWitnet(_witnetRequestBoard) {
        emit WrbSet(_witnetRequestBoard);
    }

    /// @notice Allows this contract to receive Ether
    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    /// @notice Allows the owner of this contract to withdraw Ether
    function refund() external onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
    }

    /// @notice Allows owner to set the maximum fee per request (in wei) a Witnet RNG can spend
    /// @notice The remainder of the fee will be payed back after the request has been sent
    /// @param _maxFee The maximum fee that can be charged by a request
    function setMaxFee(uint256 _maxFee) external onlyOwner {
        maxFee = _maxFee;

        emit MaxFeeSet(_maxFee);
    }

    /// @notice Allows owner to set the bytes for an encoded Witnet RNG request
    /// @param _request The request bytes that make up the request
    function setRequest(bytes memory _request) external onlyOwner {
        witnetRequest = new WitnetRequest(_request);

        emit RequestSet(_request);
    }

    /// @notice Allows owner to add an address which can generate an RNG request
    /// @param _requester The address that can generate an RNG request
    function addAllowedRequester(address _requester) external onlyOwner {
        allowedRequester[_requester] = true;

        emit RequesterAdded(_requester);
    }

    /// @notice Gets the last request id used by the RNG service
    /// @return requestId The last request id used in the last request
    function getLastRequestId() external view override returns (uint32 requestId) {
        return requestCount;
    }

    /// @notice Gets the maximum fee for making a request against an RNG service
    /// @return feeToken Compatibility return value: no fee token is required but payed in Ether
    /// @return requestFee The maximum fee required for making a request
    function getRequestFee() external view override returns (address feeToken, uint256 requestFee) {
        return (address(0), maxFee);
    }

    /// @notice Sends a request for a random number to the 3rd-party service
    /// @dev Some services will complete the request immediately, others may have a time-delay
    /// @return requestId The ID of the request used to get the results of the RNG service
    /// @return lockBlock The block number at which the RNG service will start generating time-delayed randomness. The calling contract
    /// should "lock" all activity until the result is available via the `requestId`
    function requestRandomNumber() external override returns (uint32 requestId, uint32 lockBlock) {
        require(allowedRequester[msg.sender], "RngWitnet/requester-not-allowed");

        lockBlock = uint32(block.number);

        requestId = _requestRandomness();

        requestLockBlock[requestId] = lockBlock;

        emit RandomNumberRequested(requestId, msg.sender);
    }

    /// @notice Checks if the request for randomness has completed and the random number can be fetched
    /// @param requestId The ID of the request used to get the results of the RNG service
    /// @return isFetchable True if the request has completed and a random number can be fetched
    function isRngFetchable(uint32 requestId) external view returns (bool isFetchable) {
        uint _queryId = witnetRequestIds[requestId];
        return _queryId != 0 && _witnetCheckResultAvailability(_queryId);
    }

    /// @notice Checks if the request for randomness from the 3rd-party service has completed and has been fetched
    /// @dev For time-delayed requests, this function is used to check/confirm completion
    /// @param requestId The ID of the request used to get the results of the RNG service
    /// @return isCompleted True if the request has completed and a random number is available, false otherwise
    function isRequestComplete(uint32 requestId) external view override returns (bool isCompleted) {
        uint _queryId = witnetRequestIds[requestId];
        return _queryId != 0 && _witnetCheckResultAvailability(_queryId) && randomNumberFetched[requestId];
    }

    /// @notice Gets the random number produced by the 3rd-party service
    /// @param requestId The ID of the request used to get the results of the RNG service
    /// @return randomNum The random number
    function randomNumber(uint32 requestId) external view override returns (uint256 randomNum) {
        return randomNumbers[requestId];
    }

    /// @dev Requests a new random number from the Chainlink VRF
    /// @dev The result of the request is returned in the function `fulfillRandomness`
    function _requestRandomness() internal returns (uint32 requestId) {
        require(witnetRequest.bytecode().length != 0, "RngWitnet/request-not-set");

        uint256 _witnetReward = _witnetEstimateReward();
        require(_witnetReward < maxFee, "RngWitnet/max-fee-too-low");
        require(address(this).balance >= _witnetReward, "RngWitnet/balance-too-low");

        // Get next request ID
        requestId = _getNextRequestId();

        // Post the raw randomness request
        uint256 _witnetQueryId = witnet.postRequest{value: _witnetReward}(witnetRequest);

        // Save a mapping of internal query ids to Witnet query ids
        witnetRequestIds[requestId] = _witnetQueryId;

        // Transfer back unused funds
        if (_witnetReward < maxFee) {
            payable(address(this)).transfer(maxFee - _witnetReward);
        }

        emit RngRequested(requestId, _witnetQueryId);
    }

    /// @notice Function to fetch randomness once it is ready
    /// @dev Check if the result of the randomness function is ready and return the value if it is
    function fetchRandomness(uint32 requestId) external
    {
        uint _queryId = witnetRequestIds[requestId];

        // Check whether the randomness request has already been resolved
        require(_witnetCheckResultAvailability(_queryId), "RngWitnet/randomness-not-available");

        // Low-level interaction with the WitnetRequestBoard as to deserialize the result,
        // and check whether the randomness request failed or succeeded:
        Witnet.Result memory _result = witnet.readResponseResult(_queryId);
        if (_result.success) {
            uint256 randomness = uint256(witnet.asBytes32(_result));
            randomNumbers[requestId] = randomness;
            randomNumberFetched[requestId] = true;
            emit RandomNumberCompleted(requestId, randomness);
        } else {
            emit RandomNumberFailed(requestId);
        }
    }

    /// @dev Gets the next consecutive request ID to be used
    /// @return requestId The ID to be used for the next request
    function _getNextRequestId() internal returns (uint32 requestId) {
        requestCount++;
        requestId = requestCount;
    }
}

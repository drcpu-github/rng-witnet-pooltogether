from web3 import Web3

# RngWitnet
disallowedRequester = Web3.keccak(text='disallowedRequester(address)')[:4].hex()
maxFeeTooLow = Web3.keccak(text='maxFeeTooLow(uint256,uint256)')[:4].hex()
balanceTooLow = Web3.keccak(text='balanceTooLow(uint256,uint256)')[:4].hex()
randomnessNotAvailable = Web3.keccak(text='randomnessNotAvailable(uint256)')[:4].hex()

# WitnetRequestMalleableBase
requestAlreadyInitialized = Web3.keccak(text='requestAlreadyInitialized()')[:4].hex()
noWitnessingReward = Web3.keccak(text='noWitnessingReward()')[:4].hex()
invalidNumWitnesses = Web3.keccak(text='invalidNumWitnesses(uint8)')[:4].hex()
invalidWitnessingConsensus = Web3.keccak(text='invalidWitnessingConsensus(uint8)')[:4].hex()
invalidWitnessingCollateral = Web3.keccak(text='invalidWitnessingCollateral(uint64)')[:4].hex()

def main():
    print(f"disallowedRequester: {disallowedRequester}")
    print(f"maxFeeTooLow: {maxFeeTooLow}")
    print(f"balanceTooLow: {balanceTooLow}")
    print(f"randomnessNotAvailable: {randomnessNotAvailable}")

    print(f"requestAlreadyInitialized: {requestAlreadyInitialized}")
    print(f"noWitnessingReward: {noWitnessingReward}")
    print(f"invalidNumWitnesses: {invalidNumWitnesses}")
    print(f"invalidWitnessingConsensus: {invalidWitnessingConsensus}")
    print(f"invalidWitnessingCollateral: {invalidWitnessingCollateral}")

if __name__ == "__main__":
    main()
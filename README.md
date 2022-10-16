## Introduction

The `RngWitnet.sol` contract is based on the RNGInterface contract provided by PoolTogether. Its goal is to fetch a single random number once a prize draw is completed. The cost for the RNG request is paid from the balance of the RNG contract.

## Scripts

A `deploy.py` script has been added to deploy the contract which requires a single argument (the WitnetRequestBoard address) in its constructor.

A set of scripts are provided to set some of the variables in the `RngWitnet.sol` contract:
1. `set_max_fee.py`: used to the maximum fee to fetch a random number.
2. `set_request.py`: sets the bytecode for a Witnet request.
3. `add_allowed_requester.py`: add an address which can be used to fetch a random number.
4. `fetch_rng.py`: serves as an example of automatically cycling through a complete RNG request.

## Command line examples

Deploy the contract. The `WitnetRequestBoard` address which is dependent on the network can be configured in `config.json`.
```
brownie run deploy.py deploy_goerli --network goerli-alchemy
```

Set the maximum allowed fee. This fee can be configured in `config.json`.
```
brownie run set_max_fee.py --network goerli-alchemy
```

Set the Witnet request bytecode. This can be configured in `config.json`. The currently configured request can be found in `requests/RNG.js`. This request can be modified as required and encoded as bytecode using the `witnet-requests` npm distribution.
```
brownie run set_request.py --network goerli-alchemy
```

Add one or more addresses that are allowed to fetch random numbers. This can be configured in `config.json`.
```
brownie run add_allowed_requester.py add_requesters_goerli --network goerli-alchemy
```

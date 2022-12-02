# Introduction

The `RngWitnet.sol` suite of contracts is an extension of the RNGInterface contract provided by PoolTogether. Its goal is to fetch a single random number to complete a prize draw. To achieve this it leverages the Witnet Randomness Oracle. The cost for the RNG request is paid from the balance of the RngWitnet contract.

## Deploy workflow

Following command line examples will help you setup the RngWitnet suite on the Goerli network. Because Brownie does not allow passing parameters to its scripts, I use a `config.json` file to pass them.

### Deploy the contracts

First deploy a `WitnetRequestRandomness` instance. If an instance already exists, the address of this instance can be specified in `config.json` and the `RngWitnet` contract will create a clone which is significantly cheaper. Once deployed, make sure to add the isntance's address to the `config.json` file.
```
brownie run deploy_witnet_request_randomness --network goerli-alchemy
```

After deploying a `WitnetRequestRandomness` instance or specifying a previously deployed instance, you can deploy the `RngWitnet` instance. Note that an instance of the `WitnetRequestBoard` needs to be configured in `config.json` and its address varies per network. For testing purposes (see below), the `main` function allows passing the address of a `WitnetRequestRandomness` instance, but this is irrelevant when actually deploying the contracts.
```
brownie run deploy_rng_witnet --network goerli-alchemy
```

### Configure the contract parameters

Set the maximum amount of ETH that can be spent on a single randomness request. This fee can be configured in `config.json`.
```
brownie run set_max_fee.py --network goerli-alchemy
```

Add one or more addresses that are allowed to fetch random numbers. These can be configured in `config.json`.
```
brownie run add_allowed_requester.py --network goerli-alchemy
```

## Testing

A set of tests has been included to test both the RngWitnet contract and the WitnetRequestRandomness contract. They can be run through the following command:
```
brownie test --disable-warnings
```

Note the usage of `--disable-warnings` to prevent `eth-utils` warnings polluting the output. Remove the flag if you want to see them.

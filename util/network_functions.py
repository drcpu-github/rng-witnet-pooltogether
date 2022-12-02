from brownie import accounts, config, network

LOCAL_BLOCKCHAINS = [
    "ethereum-fork-infura",
    "ethereum-fork-alchemy",
    "goerli-fork-alchemy",
    "development",
]

TESTNET_BLOCKCHAINS = [
    "goerli-alchemy",
]

def is_local_network():
    if network.show_active() in LOCAL_BLOCKCHAINS:
        return True
    return False

def is_testnet():
    if network.show_active() in TESTNET_BLOCKCHAINS:
        return True
    return False

def get_network():
    current_network = network.show_active()
    if current_network == "development":
        return current_network
    else:
        return "-".join(current_network.split("-")[:-1])

def get_account(index=0):
    if is_local_network():
        return accounts[index]
    else:
        if is_testnet():
            accounts.add(config["wallets"]["from_key_goerli"])
        else:
            accounts.add(config["wallets"]["from_key_ethereum"])
        return accounts[0]

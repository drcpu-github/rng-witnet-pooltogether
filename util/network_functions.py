from brownie import accounts, config, network

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "ethereum-fork-infura",
    "ethereum-fork-alchemy",
    "goerli-fork-alchemy"
]

def is_local_network():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return True
    return False

def get_network():
    current_network = network.show_active()
    return "-".join(current_network.split("-")[:2])

def get_account(index):
    if is_local_network():
        return accounts[index]
    else:
        accounts.add(config["wallets"]["from_key"])
        return accounts[index]

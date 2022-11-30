import logging
import os
import time

from web3 import Web3

from web3.middleware import geth_poa_middleware

# This function is tailored to fetch iterative events from Alchemy and won't work with another node API provider such as Infura
def get_events_alchemy(event, from_block, to_block):
    logging.info(f"Fetching {event.event_name} events from block {from_block} to block {to_block}")
    event_filter = event.createFilter(fromBlock=from_block, toBlock=to_block)
    try:
        return event_filter.get_all_entries()
    except ValueError as err:
        if "message" in err.args[0] and "Log response size exceeded." in err.args[0]["message"]:
            logging.warning(f"Could not fetch all {event.event_name} events at once, falling back to iterative event fetching")
            return _get_events_iteratively_alchemy(event, from_block, to_block)
        else:
            raise

# This function is tailored to fetch iterative events from Alchemy and won't work with another node API provider
def _get_events_iteratively_alchemy(event, from_block, to_block, blocks_per_call=100000):
    logging.info(f"Fetching {event.event_name} events iteratively from {from_block} to {to_block} limited to {blocks_per_call} blocks")
    events = []
    for block in range(from_block, to_block, blocks_per_call):
        fetch_until = min(to_block, block + blocks_per_call)
        logging.info(f"Fetching {event.event_name} events for block {block} to {fetch_until} (fetching until block {to_block})")
        event_filter = event.createFilter(fromBlock=block, toBlock=fetch_until)
        try:
            events.extend(event_filter.get_all_entries())
        except ValueError as err:
            if "message" in err.args[0] and "Log response size exceeded." in err.args[0]["message"]:
                logging.warning(f"Could not fetch all events at once, falling back to iterative event fetching")
                events.extend(get_events_iteratively(event, block, to_block, blocks_per_call=int(blocks_per_call / 2)))
                break
            else:
                raise
        time.sleep(0.2)
    return events

def setup_web3_provider(network, provider):
    logging.info(f"Setting up web3 provider for {network}")

    w3_provider = None
    if network == "ethereum":
        if provider == "infura":
            WEB3_ETHEREUM_INFURA = os.getenv("WEB3_ETHEREUM_INFURA")
            w3_provider = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{WEB3_ETHEREUM_INFURA}"))
        elif provider == "alchemy":
            WEB3_ETHEREUM_ALCHEMY = os.getenv("WEB3_ETHEREUM_ALCHEMY")
            w3_provider = Web3(Web3.HTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ETHEREUM_ALCHEMY}"))
    elif network == "goerli":
        if provider == "infura":
            WEB3_GOERLI_INFURA = os.getenv("WEB3_GOERLI_INFURA")
            w3_provider = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{WEB3_GOERLI_INFURA}"))
        elif provider == "alchemy":
            WEB3_GOERLI_ALCHEMY = os.getenv("WEB3_GOERLI_ALCHEMY")
            w3_provider = Web3(Web3.HTTPProvider(f"https://eth-goerli.g.alchemy.com/v2/{WEB3_GOERLI_ALCHEMY}"))
    elif network == "polygon":
        if provider == "infura":
            WEB3_POLYGON_INFURA = os.getenv("WEB3_POLYGON_INFURA")
            w3_provider = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{WEB3_POLYGON_INFURA}"))
        elif provider == "alchemy":
            WEB3_POLYGON_ALCHEMY = os.getenv("WEB3_POLYGON_ALCHEMY")
            w3_provider = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.g.alchemy.com/v2/{WEB3_POLYGON_ALCHEMY}"))
        w3_provider.middleware_onion.inject(geth_poa_middleware, layer=0)

    assert w3_provider, "Could not configure Web3 provider"
    return w3_provider

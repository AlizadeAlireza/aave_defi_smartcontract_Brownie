from brownie import network, accounts, config


LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "local-ganache",
    "mainnet-fork",
    "hardhat",
    "ganache",
]


def get_account(index=None, id=None):
    """when we call get_account() in our scripts
    it actually knows that it's a local environment that we're
    working with and it will just return account zero
    instead of us having to actually load a private key
    in every single time"""
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None

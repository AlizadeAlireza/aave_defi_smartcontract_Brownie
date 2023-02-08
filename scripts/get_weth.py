from brownie import accounts, interface, config, network
from scripts.helpful_scripts import get_account


def main():
    get_weth()


def get_weth():
    """mints WETH by depositing ETH."""
    # ABI
    # ADDRESS
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"]
    )  # we have an abi from interface
    # why aren't using get_contract() here?
    # because we're going to be testing on mainnet fork here in know
    # that we're always going to refer back to the config
    # now we can just call deposit func() where we can deposit eth and get weth
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx

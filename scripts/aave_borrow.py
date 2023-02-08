from scripts.helpful_scripts import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    # do our erc20 address because the web token is in erc20
    # and maybe we want to deposit it
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # get_weth() --> if we want to test this though on our local mainnet fork
    # we probably will want to call this get_weth()
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # ABI
    # ADDRESS
    lending_pool = get_lending_pool()
    # print(lending_pool)
    # approve sending out ERC20 tokens
    approve_erc20(
        AMOUNT, lending_pool.address, erc20_address, account
    )  # spender is going to be this lending pool and we want just the address
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )  # this will be the address of the dai

    # we can calculate the amount of dai that we want to borrow
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth ---> borrowable_dai * 95%
    print(f"we are going to borrow {amount_dai_to_borrow} DAI")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("we borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    repay_all(AMOUNT, lending_pool, account)
    print("you just deposited, borrowed, and repayed with aave, brownie, chainlink ")


def repay_all(AMOUNT, lending_pool, account):
    approve_erc20(
        Web3.toWei(AMOUNT, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        AMOUNT,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("repayed...")


def get_asset_price(price_feed_address):
    # ABI
    # ADDRESS
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    # dai_eth_price_feed is going to be a contract that
    # we can call a function on

    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)
    # 0.000000000099990000


def get_borrowable_data(lending_pool, account):
    """we're looking to call this function on the lending_pool
    from an account"""
    (
        total_collateral_eth,
        total_debt_eth_,
        available_borrow_eth,  # figure out how much we can borrow
        current_liquidation_treshhold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # is a view func so we don't need to spend any gas
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth_, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_lending_pool():
    """we're going to get the lending pool address and the lending pool contract
    so we can interact with it"""
    # ABI
    # Address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # now that we have this address we can actually return the lending pool contract
    # by once again getting the abi and address of the actual lending pool
    # ABI
    # ADDRESS - Check!
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
    # approve sending our ERC20 tokens


def approve_erc20(
    amount, spender, erc20_address, account
):  # in IERC20.sol ---> approve func
    """we have an approved erc20 function that we can use to
    approve any erc20 token"""
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(
        spender, amount, {"from": account}
    )  # we're gonna approve this spender for an amount
    tx.wait(1)
    print("Approved!")
    return tx
    # ABI
    # ADDRESS

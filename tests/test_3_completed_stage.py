from brownie import accounts, chain, reverts
from brownie.test import given, strategy
from scripts.deploy import deploy_and_fund_auction

from conftest import (
    STANDARD_TEST_TOKEN_COUNT,
    STANDARD_TEST_START_DELAY,
    STANDARD_TEST_DURATION,
    STANDARD_TEST_START_PRICE,
    STANDARD_TEST_RESERVATION_PRICE,
    STANDARD_TEST_END_MAX_CHECK_DELAY
)

# Completed auction stage tests *************************************************************************************************


@given(
    seller_account   = strategy('address'),
    relaunch_account = strategy('address')
)
def test_relaunch(test_token, seller_account, relaunch_account):
    """
        Tests that the auction cannot be launched after completion by anyone.
    """

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    launch_tx = dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
    launch_tx.wait(1)

    chain.sleep(STANDARD_TEST_START_DELAY + STANDARD_TEST_DURATION)
    chain.mine()
    
    assert(dutch_auction.hasAuctionFinished())

    with reverts():
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": relaunch_account})


@given(
    initial_buy_delay = strategy('uint32', min_value=STANDARD_TEST_START_DELAY, max_value=STANDARD_TEST_START_DELAY + STANDARD_TEST_DURATION),
    after_completion_buy_delay = strategy('uint32', min_value=0, max_value=STANDARD_TEST_END_MAX_CHECK_DELAY),
)
def test_buy(test_token, initial_buy_delay, after_completion_buy_delay):
    """
        Tests that a bid price cannot be returned by the auction nor that a bid can be placed after the auction completes
    """
    seller_account = accounts[0]
    buyer_account  = accounts[1]

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    launch_tx = dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
    launch_tx.wait(1)

    chain.sleep(initial_buy_delay)
    chain.mine()

    buy_timestamp = chain.time()
    # If auction is deserted (as the initial buy is after the auction bidding time)
    if buy_timestamp >= end_timestamp:
        with reverts():
            dutch_auction.buy({"from": buyer_account, "value": start_price})
    # If a buyer makes a successful bid
    else:
        buyTx = dutch_auction.buy({"from": buyer_account, "value": start_price})
        buyTx.wait(1)

    # After the auction completes
    chain.sleep(end_timestamp - chain.time() + after_completion_buy_delay)
    chain.mine()

    assert(dutch_auction.hasAuctionFinished())

    # Buy should always fail
    with reverts():
        dutch_auction.getCurrentPrice()
    with reverts():
        dutch_auction.buy({"from": buyer_account, "value": start_price})



@given(
    buyDelay = strategy('uint32', min_value=STANDARD_TEST_START_DELAY, max_value=STANDARD_TEST_START_DELAY + STANDARD_TEST_DURATION + STANDARD_TEST_END_MAX_CHECK_DELAY),
)
def test_retrieve_tokens(test_token, buyDelay):
    """
        Tests that the auctioned tokens can be retrieved by the seller (if available).
    """

    seller_account = accounts[0]
    buyer_account  = accounts[1]

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    launch_tx = dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
    launch_tx.wait(1)

    chain.sleep(buyDelay)
    chain.mine()

    buy_timestamp = chain.time()
    auctionDeserted = False

    # If the auction is deserted
    if buy_timestamp >= end_timestamp:
        with reverts():
            dutch_auction.buy({"from": buyer_account, "value": start_price})
        auctionDeserted = True

    # If a buyer places a valid bid
    else:
        buyTx = dutch_auction.buy({"from": buyer_account, "value": start_price})
        buyTx.wait(1)

    assert(auctionDeserted == dutch_auction.isAuctionDeserted())

    # Check tokens
    sellerTokenBalance = test_token.balanceOf(seller_account)
    dutch_auction.retrieveTokens({"from": seller_account})
    newSellerTokenBalance = test_token.balanceOf(seller_account)
    assert(
        newSellerTokenBalance == sellerTokenBalance + (STANDARD_TEST_TOKEN_COUNT if auctionDeserted else 0)
    )



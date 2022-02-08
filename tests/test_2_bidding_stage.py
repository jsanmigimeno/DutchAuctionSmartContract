from brownie import accounts, chain, reverts
from brownie.test import given, strategy
from scripts.deploy import deploy_and_fund_auction

from conftest import (
    STANDARD_TEST_TOKEN_COUNT,
    STANDARD_TEST_START_DELAY,
    STANDARD_TEST_DURATION,
    STANDARD_TEST_START_PRICE,
    STANDARD_TEST_RESERVATION_PRICE,
    STANDARD_TEST_PRICE_CHECK_MARGIN
)

# Bidding auction stage tests ***************************************************************************************************


@given(
    buyDelayAfterDeploy = strategy('uint32', min_value=0, max_value=STANDARD_TEST_START_DELAY + STANDARD_TEST_DURATION),
    buyPriceDelta       = strategy('int256', min_value=-STANDARD_TEST_START_PRICE, max_value=STANDARD_TEST_START_PRICE)
)
def test_buy_time_and_price(test_token, buyDelayAfterDeploy, buyPriceDelta):
    """
        Tests the time and price when placing a bid to the auction.
    """

    seller_account            = accounts[0]
    seller_start_balance      = seller_account.balance()

    buyer_account             = accounts[1]
    buyer_start_balance       = buyer_account.balance()
    buyer_start_token_balance = test_token.balanceOf(buyer_account)

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    launch_tx = dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
    launch_tx.wait(1)

    # Simulate time delay
    chain.sleep(buyDelayAfterDeploy)
    chain.mine()

    buy_timestamp = chain.time()

    # If the auction isn't active, a bid price shouldn't be returned
    if buy_timestamp < start_timestamp or buy_timestamp >= end_timestamp:
        with reverts():
            dutch_auction.getCurrentPrice()
        return
    
    # Compare the returned bid price with a calculated one. Note that a small error defined by 
    # STANDARD_TEST_PRICE_CHECK_MARGIN is allowed
    auctionPrice = dutch_auction.getCurrentPrice()

    ellapsedTime = buy_timestamp - start_timestamp
    expectedPriceMax = start_price - int((start_price - reservation_price)/(end_timestamp - start_timestamp)*(ellapsedTime - STANDARD_TEST_PRICE_CHECK_MARGIN))
    expectedPriceMin = start_price - int((start_price - reservation_price)/(end_timestamp - start_timestamp)*(ellapsedTime + STANDARD_TEST_PRICE_CHECK_MARGIN))
    
    assert (auctionPrice <= expectedPriceMax and auctionPrice >= expectedPriceMin)


    # Place a bid
    buy_price = max(auctionPrice + buyPriceDelta, 0) # Modify the bid price by buyPriceDelta

    bought_price = 0

    try:
        buyTx = dutch_auction.buy({"from": buyer_account, "value": buy_price})
        buyTx.wait(1)

        bought_price = buyTx.return_value # Get the actual price payed

    except:
        # If the bid was invalid
        if buy_timestamp >= end_timestamp or buy_price < auctionPrice: return

        # If the bid was valid
        else: raise Exception('Should not have reverted')

    # If the bid was invalid
    if bought_price > buy_price: raise Exception('Insufficient funds, Should have reverted.')


    # Check seller got funds
    assert(seller_account.balance() == seller_start_balance + bought_price)

    # Check buyer got tokens + excess refund
    assert(buyer_account.balance() == buyer_start_balance - bought_price)
    assert(test_token.balanceOf(buyer_account) == buyer_start_token_balance + STANDARD_TEST_TOKEN_COUNT)


@given(
    seller_account = strategy('address'),
    buyer_account  = strategy('address')
)
def test_buyer(test_token, seller_account, buyer_account):
    """
        Tests that the buyer is not the seller.
    """

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})

    # Simulate time delay
    chain.sleep(STANDARD_TEST_START_DELAY)
    chain.mine()

    # If launch shouldn't be successful
    if seller_account == buyer_account:
        with reverts():
            dutch_auction.buy({"from": buyer_account, "value": start_price})

    # If launch should be successful
    else:
        dutch_auction.buy({"from": buyer_account, "value": start_price})


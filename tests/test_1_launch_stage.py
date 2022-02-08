from brownie import accounts, chain, reverts
from brownie.test import given, strategy
from scripts.deploy import deploy_and_fund_auction

from conftest import (
    STANDARD_TEST_TOKEN_COUNT,
    STANDARD_TEST_START_DELAY,
    STANDARD_TEST_DURATION,
    STANDARD_TEST_START_PRICE,
    STANDARD_TEST_RESERVATION_PRICE
)

# Launch auction stage tests ****************************************************************************************************


@given(
    start_timestamp_delta = strategy('int256', min_value=-3600*12, max_value=3600*12),
    end_timestamp_delta   = strategy('int256', min_value=-3600*12, max_value=3600*12),
)
def test_launch_timestamps(test_token, start_timestamp_delta, end_timestamp_delta):
    """
        Tests the start and end timestamps when launching the auction.
    """

    seller_account = accounts[0]

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + start_timestamp_delta
    end_timestamp     = current_timestamp + end_timestamp_delta
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE


    # If launch shouldn't be successful
    if start_timestamp <= current_timestamp or end_timestamp <= start_timestamp:
        
        with reverts():
            dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
    
    # If launch should be successful
    else:
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})

        assert(dutch_auction.startTimestamp() == start_timestamp)
        assert(dutch_auction.endTimestamp() == end_timestamp)


@given(
    start_price       = strategy('int256', min_value=0, max_value=STANDARD_TEST_START_PRICE),
    reservation_price = strategy('int256', min_value=0, max_value=STANDARD_TEST_START_PRICE)
)
def test_launch_prices(test_token, start_price, reservation_price):
    """
        Tests the start and reservation price when launching the auction.
    """

    seller_account = accounts[0]

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION

    # If launch shouldn't be successful
    if start_price == 0 or reservation_price >= start_price:
        with reverts():
            dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})

    # If launch should be successful
    else:
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})

        assert(dutch_auction.startPrice() == start_price)
        assert(dutch_auction.reservationPrice() == reservation_price)


@given(
    auction_token_count = strategy('int256', min_value=0, max_value=STANDARD_TEST_TOKEN_COUNT)
)
def test_launch_token_count(test_token, auction_token_count):
    """
        Tests a correct funding (with tokens) of the auction when launching the auction.
    """

    seller_account = accounts[0]

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, auction_token_count)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    # If launch shouldn't be successful
    if auction_token_count == 0:
        with reverts():
            dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
        
        # Tokens should be recoverable (albeit in this test case it doesn't make much sense)
        dutch_auction.retrieveTokens({"from": seller_account})
        assert(test_token.balanceOf(seller_account) == auction_token_count)

    # If launch should be successful
    else:
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})
        assert(dutch_auction.getTokenBalance() == auction_token_count)

        # Tokens should not be recoverable
        with reverts():
            dutch_auction.retrieveTokens({"from": seller_account})        



@given(
    seller_account = strategy('address'),
    launch_account = strategy('address')
)
def test_launch_account(test_token, seller_account, launch_account):
    """
        Tests the address that launches the auction.
    """

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    # If launch shouldn't be successful
    if seller_account != launch_account:
        with reverts():
            dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": launch_account})

    # If launch should be successful
    else:
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": launch_account})


@given(
    seller_account   = strategy('address'),
    relaunch_account = strategy('address')
)
def test_relaunch(test_token, seller_account, relaunch_account):
    """
        Tests that the auction cannot be relaunched by anyone.
    """

    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    current_timestamp = chain.time()
    start_timestamp   = current_timestamp + STANDARD_TEST_START_DELAY
    end_timestamp     = start_timestamp   + STANDARD_TEST_DURATION
    start_price       = STANDARD_TEST_START_PRICE
    reservation_price = STANDARD_TEST_RESERVATION_PRICE

    dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": seller_account})

    # Relaunch should always fail
    with reverts():
        dutch_auction.launchAuction(start_timestamp, end_timestamp, start_price, reservation_price, {"from": relaunch_account})

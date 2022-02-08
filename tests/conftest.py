from pytest import fixture
from brownie import accounts, TestToken, DutchAuction, network, config
from web3 import Web3

STANDARD_TEST_START_DELAY         = 3600*24*3               # Delay to start the auction (from chain.time() - in seconds)
STANDARD_TEST_DURATION            = 3600*24*7               # Auction duration (in seconds)
STANDARD_TEST_START_PRICE         = Web3.toWei(10, "gwei")  # Auction start price
STANDARD_TEST_RESERVATION_PRICE   = Web3.toWei(1, "gwei")   # Auction reservation price
STANDARD_TEST_TOKEN_COUNT         = 1000                    # Auctioned tokens count
STANDARD_TEST_PRICE_CHECK_MARGIN  = 15                      # Allowed margin for auction price check (in seconds)
STANDARD_TEST_END_MAX_CHECK_DELAY = 3600*1                  # Max margin for checks after auction completion


@fixture(autouse=True)
def shared_setup(fn_isolation):
    pass


@fixture(scope="module")
def test_token():
    if len(TestToken) <= 0:
        TestToken.deploy("TestToken", "TT", {"from": accounts[0]})
    
    return TestToken[-1]

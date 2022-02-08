from brownie import accounts, reverts
from brownie.test import given, strategy
from scripts.deploy import deploy_and_fund_auction

from conftest import STANDARD_TEST_TOKEN_COUNT

# Misc tests ********************************************************************************************************************


def test_send_funds_to_contract(test_token):
    """
        Tests that ETH cannot be sent to the contract via a transfer call.
    """

    seller_account = accounts[0]
    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    with reverts():
        seller_account.transfer(dutch_auction, 1)


@given(
    seller_account  = strategy('address'),
    recover_account = strategy('address')
)
def test_recover_funds_from_contract(test_token, seller_account, recover_account):
    """
        Tests that ETH can be recovered by the seller (precaution).
    """
    dutch_auction = deploy_and_fund_auction(seller_account, test_token, STANDARD_TEST_TOKEN_COUNT)

    # If fund recovering shouldn't be allowed
    if seller_account != recover_account:
        with reverts():
            dutch_auction.retrieveFunds({"from": recover_account})
    
    # If fund recovering should be allowed
    else: dutch_auction.retrieveFunds({"from": recover_account})
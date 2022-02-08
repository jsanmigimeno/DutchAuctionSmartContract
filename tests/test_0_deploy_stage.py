from brownie import DutchAuction, accounts, config, network, reverts
from brownie.test import given, strategy

from conftest import STANDARD_TEST_TOKEN_COUNT


# Deploy auction stage tests ****************************************************************************************************


def test_deploy(test_token):
    """
        Test a successful deployment of the dutch_auction contract.
    """

    seller_account = accounts[0]

    DutchAuction.deploy(test_token, {"from": seller_account})


@given(
    seller_account        = strategy('address'),
    token_recover_account = strategy('address'),
    auction_token_count   = strategy('int256', min_value=0, max_value=STANDARD_TEST_TOKEN_COUNT)
)
def test_token_fund(test_token, seller_account, token_recover_account, auction_token_count):
    """
        Tests that a deployed contract can be funded with tokens, and its funds be recovered by the seller.
    """

    dutch_auction = DutchAuction.deploy(test_token, {"from": seller_account})

    assert(dutch_auction.getTokenBalance() == 0)

    # Fund the auction with tokens
    test_token.getTokens(auction_token_count, {"from": dutch_auction})
    assert(dutch_auction.getTokenBalance() == auction_token_count)

    # If recovering tokens shouldn't be allowed
    if seller_account != token_recover_account:
        with reverts():
            dutch_auction.retrieveTokens({"from": token_recover_account})
    
    # Recovering tokens should be allowed
    else:
        dutch_auction.retrieveTokens({"from": token_recover_account})
        assert(test_token.balanceOf(seller_account) == auction_token_count)


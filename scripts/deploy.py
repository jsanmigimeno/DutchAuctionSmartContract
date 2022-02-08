from brownie import DutchAuction, network, config

def deploy_auction(account, token):
    return DutchAuction.deploy(token, {"from": account})

def deploy_and_fund_auction(account, token, tokenCount):
    auction = deploy_auction(account, token)

    token.getTokens(tokenCount, {"from": account})
    token.transfer(auction, tokenCount, {"from": account})

    return auction


def main():
    pass
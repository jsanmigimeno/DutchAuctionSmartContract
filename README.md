# Dutch Auction Smart Contract - Winner Takes It All
In this implementation of the Dutch Auction, tokens provided by the owner of the contract are auctioned. The contract follows these stages:
1. The seller deploys the **DutchAuction** contract.
2. The seller transfers **ERC20** tokens to the contract.
3. The seller launches the contract, providing:
    - The start timestamp (UNIX timestamp)
    - The end timestamp (UNIX timestamp)
    - The start price (in Wei)
    - The reservation price (minimum sell price - in Wei)
4. Whilst the auction is ongoing, the first buyer to place a valid bid will automatically receive the auctioned tokens, plus a refund if excess funds where transfered to the contract. The seller will also automatically receive the funds payed by the buyer.
5. If the auction is deserted, the seller may retrieve the deposited tokens.

Note that by design, the contract is not reusable.


<br>

# Solidity and Dependencies
The Dutch Auction smart contract is implemented with Solidity 0.8.0.

The only dependency used by this Dutch Auction contract is OpenZeppelin/openzeppelin-contracts@4.4.2, which is installed via brownie's package manager:

    brownie pm install OpenZeppelin/openzeppelin-contracts@4.4.2


<br>

# Dutch Auction Smart Contract Interface
The smart contract has the following interface:
    

### Auction State Functions
- `isAuctionReady() public view returns (bool)`
    - Check whether the auction has been launched (note that the auction may not have necessarily started)
- `hasAuctionStarted() public view returns (bool)`
    - Check whether the auction has started
- `hasAuctionFinished() public view returns (bool)`
    - Check whether the auction has finished
- `isAuctionOngoing() public view returns (bool)`
    - Check whether the auction is ongoing (i.e. accepting bids)
- `isAuctionDeserted() public view returns (bool)`
    - Check whether there was no winning bid. It can only be called after the auction has finished.

### Seller Functions
- `launchAuction(uint256 _startTimestamp, uint256 _endTimestamp, uint256 _startPrice, uint256 _reservationPrice) external onlyOwner`
    - Launches the auction with the provided parameters. The contract must be funded with tokens (to be auctioned) before launching the auction.
- `retrieveTokens() external onlyOwner`
    - Transfers all the tokens from the contract to the seller. It can only be called before the auction is launched or after it finishes.
- `retrieveFunds() external payable onlyOwner`
    - Transfers all the ETH funds from the contract to the seller. This is a precaution; it should never be required as the contract should never hold ETH funds.

### Public/External Functions
- `getCurrentPrice() public view returns (uint256)`
    - Get the price of the current bid. It can only be called whilst the auction is ongoing.
- `buy() external payable returns (uint256)`
    - Place a bid. It can only be called whilst the auction is ongoing and cannot be called by the seller.
- `getTokenBalance() public view returns (uint256)`
    - Get the balance of the tokens available to the contract to auction.


<br>
For examples on how to use the contract, see the provided tests (in the tests folder).

<br>

# Testing
During testing, a mock ERC20 token, **TestToken**, is deployed; a simple token which will provide free tokens to whomever requests them.

Most of the tests providaded are property based.

Testing of the Dutch Auction is seprated in 5 stages:
1. Deploy stage
2. Launch stage
3. Bidding stage
4. Completed stage
5. Miscellaneous tests (tests which do not depend on the stage of the contract)

Testing has been executed locally using Brownie's built-in Ganache. Note that all tests expect the used wallets (ganache default wallets) to have enough funds. To run the tests, run:

    brownie test

All tests have been checked to pass on the following configuration:
- Arch Linux 5.15.14-1-lts
- Python: 3.8.12
- Brownie: v1.17.2
- Ganache: Ganache CLI v6.12.2 (ganache-core: 2.13.2)

Total tests execution time: 5min 47sec
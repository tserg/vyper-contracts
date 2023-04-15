# @version ^0.3.2

"""
@title Vickrey auction where winning bidder pays the second highest bid price
@license GPL-3.0
@author Gary Tse
@notice You can use this contract for a simple Vickrey auction.
@dev This contract does not handle the transfer of the underlying asset.
"""

event Bid:
	value: uint256
	bidder: indexed(address)

event Refund:
	value: uint256
	bidder: indexed(address)

owner: address

# @dev Dynamic array to track the highest two bids
top_two_bids: public(DynArray[uint256, 2])

# @dev Mapping from bid amount to bidding addresses
bids_to_bidder: public(HashMap[uint256, address])

# @dev Mapping of bidding addresses to balance held in contract
bidder_to_balance: public(HashMap[address, uint256])

START_PRICE: immutable(uint256)
DEADLINE: immutable(uint256)

# @dev Boolean for whether owner has claimed the winning bid
is_claimed: public(bool)


@external
def __init__(
	start_price: uint256,
	deadline: uint256
):

	# Deadline must be after current block
	assert deadline > block.timestamp

	START_PRICE = start_price
	DEADLINE = deadline

	self.owner = msg.sender
	self.is_claimed = False
	self.top_two_bids = [start_price, start_price]
	self.bids_to_bidder[start_price] = msg.sender


@external
@payable
def bid():
	"""
	@notice Submit a bid to the contract by sending Ether to the contract. If one or
	 	 more bids have been submitted, the new bid will be calculated based on
		 the sum of the cumulative total of previous bids and `msg.value`.
	@dev Throws if the auction deadline has passed.
		 Throws if the sum of the cumulative total of previous bids and `msg.value`
		 is not greater than the highest bid.
	"""
	assert block.timestamp <= DEADLINE, "Auction has ended"

	_previous_bid: uint256 = self.bidder_to_balance[msg.sender]
	_new_bid: uint256 = _previous_bid + msg.value

	assert _new_bid > self.top_two_bids[0], "Bid is below current price"

	self.bidder_to_balance[msg.sender] = _new_bid

	self.top_two_bids[1] = self.top_two_bids[0]
	self.top_two_bids[0] = _new_bid
	self.bids_to_bidder[_new_bid] = msg.sender

	log Bid(_new_bid, msg.sender)


@external
def close():
	"""
	@notice Close the auction and transfer the second highest bid value from the
		 winning bidder's balance to the owner of the contract.
	@dev Throws if the auction deadline has not passed
		 Throws if the auction has already closed.
	"""
	assert block.timestamp > DEADLINE, "Auction has not ended"
	assert self.is_claimed == False, "Owner has already claimed"

	if self.top_two_bids[0] > START_PRICE:
		self.is_claimed = True

		# Send 2nd highest bid amount to owner
		send(self.owner, self.top_two_bids[1])


@external
def refund():
	"""
	@notice Claim the unused balance after the auction has ended.
	@dev Throws if the auction has not closed.
		 Throws if `msg.sender` does not have any funds.
	"""
	assert block.timestamp > DEADLINE, "Auction has not closed"
	assert self.bidder_to_balance[msg.sender] > 0, "No bids from current address"

	_winner: address = self.bids_to_bidder[self.top_two_bids[0]]

	_balance: uint256 = self.bidder_to_balance[msg.sender]

	# If msg.sender is the top bidder, subtract the bid price (2nd highest bid)
	if msg.sender == _winner:
		_balance = _balance - self.top_two_bids[1]

	self.bidder_to_balance[msg.sender] = 0
	send(msg.sender, _balance)
	log Refund(_balance, msg.sender)


@external
@view
def get_highest_bid() -> uint256:
	"""
	@notice Get the current highest bid.
	@return The first value of the top two bids.
	"""
	return self.top_two_bids[0]


@external
@view
def get_second_highest_bid() -> uint256:
	"""
	@dev Get the current second highest bid.
	@return The second value of the top two bids.
	"""
	return self.top_two_bids[1]


@external
@view
def has_ended() -> bool:
	"""
	@dev Check whether the auction has ended
	@return Boolean value of whether the auction deadline has passed.
	"""
	return block.timestamp > DEADLINE

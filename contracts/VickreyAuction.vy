# @version ^0.3.2

# @dev Vickrey auction where winning bidder pays the second highest bid price

event Bid:
	value: uint256
	bidder: indexed(address)

event Refund:
	value: uint256
	bidder: indexed(address)

owner: address

top_two_bids: public(DynArray[uint256, 2])
bids_to_bidder: public(HashMap[uint256, address])
bidder_to_balance: public(HashMap[address, uint256])

START_PRICE: immutable(uint256)
DEADLINE: immutable(uint256)

is_claimed: public(bool)


@external
def __init__(
	start_price: uint256,
	deadline: uint256
):

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

	assert block.timestamp > DEADLINE, "Auction has not ended"
	assert self.is_claimed == False, "Owner has already claimed"

	if self.top_two_bids[0] > START_PRICE:
		self.is_claimed = True

		# Send 2nd highest bid amount to owner
		send(self.owner, self.top_two_bids[1])


@external
def refund():

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
	return self.top_two_bids[0]


@external
@view
def get_second_highest_bid() -> uint256:
	return self.top_two_bids[1]


@external
@view
def has_ended() -> bool:
	return block.timestamp > DEADLINE

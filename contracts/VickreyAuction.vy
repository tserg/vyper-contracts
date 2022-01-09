# @version ^0.3.0

# @dev Vickrey auction where winning bidder pays the second highest bid price

event Bid:
	value: uint256
	bidder: indexed(address)

owner: address

top_two_bids: public(DynArray[uint256, 2])
bids_to_bidder: public(HashMap[uint256, address])

START_PRICE: immutable(uint256)
DEADLINE: immutable(uint256)

is_claimed: public(bool)


@external
def __init__(
	start_price: uint256,
	deadline: uint256
):

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
	assert msg.value > self.top_two_bids[0], "Bid is below current price"

	self.top_two_bids[1] = self.top_two_bids[0]
	self.top_two_bids[0] = msg.value
	self.bids_to_bidder[msg.value] = msg.sender
	log Bid(msg.value, msg.sender)


@external
def close():

	assert block.timestamp > DEADLINE, "Auction has not ended"
	assert self.is_claimed == False, "Owner has already claimed"

	if self.top_two_bids[0] > START_PRICE:
		self.is_claimed = True
		send(self.owner, self.top_two_bids[0])


@external
@view
def get_highest_bid() -> uint256:
	return self.top_two_bids[0]


@external
@view
def has_ended() -> bool:
	return block.timestamp > DEADLINE

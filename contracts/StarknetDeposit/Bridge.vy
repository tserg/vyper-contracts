# @version ^0.3.0

"""
@title Starknet ERC-20 Bridge, adapted from official Starknet documentation
	   [https://www.cairo-lang.org/docs/hello_starknet/l1l2.html]
@license GPL-3.0
@author Gary Tse
@notice You can use this contract to deposit and withdraw an ERC-20 to and from
		Starknet.
@dev After the token is deposited in Starknet, there are currently no functions to
	 deal with them on Starknet itself. You can only withdraw back to L1 and view
	 the balance on Starknet.
"""

from vyper.interfaces import ERC20

interface IStarknetCore:

	def sendMessageToL2(
		to_address: uint256,
		selector: uint256,
		payload: uint256[4]
	) -> bytes32: nonpayable

	def consumeMessageFromL2(
		fromAddress: uint256,
		payload: uint256[3]
	) -> bytes32: nonpayable

# @dev Address of ERC-20 token
token: public(ERC20)

# @dev Address of Starknet Core contract on L1
sn_core: public(IStarknetCore)

# @dev Mapping from L2 address to balance
user_balances: HashMap[uint256, uint256]

# @dev Selector for "deposit" function
DEPOSIT_SELECTOR: constant(uint256) = 352040181584456735608515580760888541466059565068553383579463728554843487745

# @dev Starknet message
MESSAGE_WITHDRAW: constant(uint256) = 0

MAX_AMOUNT: constant(uint256) = 2 ** 64

@external
def __init__(token: address, sn_core: address):

	self.token = ERC20(token)
	self.sn_core = IStarknetCore(sn_core)


@external
def withdraw(
	l2_contract_address: uint256,
	user_l2_address: uint256,
	amount: uint256
):
	"""
	@notice Withdraw from the contract after the equivalent withdrawal transaction
			on Starknet is `ACCEPTED_ON_L1`
	@param l2_contract_address Address of the Starknet contract
	@param user_l2_address Address of the user on Starknet
	@param amount Amount to be withdrawn
	"""
	# Custom workaround pending merging of PR #2603
	# [https://github.com/vyperlang/vyper/pull/2603]
	_message_withdraw: uint256 = MESSAGE_WITHDRAW
	_offset: uint256 = 64
	_payload_size: uint256 = 4

	payload: Bytes[228] = _abi_encode(
		l2_contract_address,
		_offset,
		_payload_size,
		_message_withdraw,
		user_l2_address,
		msg.sender,
		amount,
		method_id=method_id("consumeMessageFromL2(uint256,uint256[])")
	)

	response: Bytes[32] = raw_call(
		self.sn_core.address,
		payload,
		max_outsize=32
	)

	self.token.transfer(msg.sender, amount)
	self.user_balances[user_l2_address] -= amount


@external
def deposit(
	l2_contract_address: uint256,
	user_l2_address: uint256,
	amount: uint256
) -> Bytes[32]:
	"""
	@notice Deposit to the contract for message transmission to Starknet contract
	@dev Throws if `amount` is equal to or greater than MAX_AMOUNT
		 Throws if contract is not approved to transfer the `amount` of ERC-20
	@param l2_contract_address Address of the Starknet contract
	@param user_l2_address Address of the user on Starknet
	@param amount Amount to be deposited
	@return Response of the call to Starknet core contract to transmit message to
	        Starknet
	"""
	assert amount < MAX_AMOUNT, "Invalid amount"
	assert self.token.allowance(msg.sender, self) >= amount, "Contract is not approved"

	self.token.transferFrom(msg.sender, self, amount)
	self.user_balances[user_l2_address] += amount

	_offset: uint256 = 96
	_payload_size: uint256 = 2

	# Custom workaround pending merging of PR #2603
	# [https://github.com/vyperlang/vyper/pull/2603]
	_deposit_selector: uint256 = DEPOSIT_SELECTOR

	payload: Bytes[196] = _abi_encode(
		l2_contract_address,
		_deposit_selector,
		_offset,
		_payload_size,
		user_l2_address,
		amount,
		method_id=method_id("sendMessageToL2(uint256,uint256,uint256[])")
	)

	response: Bytes[32] = raw_call(
		self.sn_core.address,
		payload,
		max_outsize=32
	)

	return response


@external
@view
def balanceOf(owner: uint256) -> uint256:
	"""
	@notice Get the balance held by the contract/deposited in Starknet for a L2 address
	@param owner Address of the L2 account
	"""
	return self.user_balances[owner]

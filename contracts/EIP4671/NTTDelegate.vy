# @version ^0.3.2

"""
@title EIP-4671 Non-Tradable Token with delegation of minting
@license GPL-3.0
@author Gary Tse
@notice You can use this contract to issue non-tradable tokens with the ability
				to mint in batches and delegate minting rights (individually or in batches).
@dev Implementation of EIP-4671
		 [https://github.com/ethereum/EIPs/blob/3fba38040b8b7fcc7ba44b85373f1e66462e3394/EIPS/eip-4671.md]
"""

event Mint:
	owner: indexed(address)
	index: uint256
	issuer: indexed(address)


event Invalidate:
	owner: indexed(address)
	index: uint256


event Delegate:
	delegate: indexed(address)
	recipient: indexed(address)


# @dev Base URI for the token
baseTokenURI: String[64]

# @dev Name of the token
name: public(String[64])

# @dev Owner of the contract
owner: address

# @dev Abbreviated name of the token
symbol: public(String[32])

# @dev Total number of issued tokens
totalSupply: public(uint256)

# @dev Mapping from address to token ID for an address to validity
ownerToIdToValidity: HashMap[address, HashMap[uint256, bool]]

# @dev Mapping from address to token ID for an address to issuer
ownerToIdToIssuer: HashMap[address, HashMap[uint256, address]]

# @dev Mapping from address to balance
ownerToBalance: HashMap[address, uint256]

# @dev Mapping from token ID to URI
ownerToIdToURI: HashMap[address, HashMap[uint256, String[64]]]

# @dev Mapping from deleagted operator address to recipient address to
# 		 delegation validity
operatorToRecipientToValidity: HashMap[address, HashMap[address, bool]]

# @dev ERC165 interface ID of ERC165
ERC165_INTERFACE_ID: constant(Bytes[32]) = b"\x01\xff\xc9\xa7"

# @dev ERC165 interface ID of EIP4671
EIP_4671_INTERFACE_ID: constant(Bytes[32]) = b"\xd2K\xe28"

# @dev ERC165 interface ID of EIP4671 Metadata
EIP_4671_METADATA_INTERFACE_ID: constant(Bytes[32]) = b"z\xf9&7"

# @dev ERC165 interface ID of EIP4671 Delegate
EIP_4671_DELEGATE_INTERFACE_ID: constant(Bytes[32]) = b"0\xbf\x86\x8c"

# @dev Maximum number of tokens that can be issued for an address
# 	   This is meant to overcome Vyper's feature of limiting range iteration and
#	   can be set to an arbitrary high value.
MAX_BALANCE: constant(uint256) = 100

# @dev Size per batch for batch minting and batch delegating
BATCH_SIZE: constant(uint256) = 3

### Constructor


@external
def __init__(
	name: String[64],
	symbol: String[32],
	baseTokenURI: String[64],
	maxBalance: uint256
):
	self.name = name
	self.symbol = symbol
	self.baseTokenURI = baseTokenURI

	self.owner = msg.sender
	self.totalSupply = 0


### Internal functions


@internal
def _setTokenURI(_owner: address, _index: uint256, _tokenURI: String[64]):
	"""
	@dev Internal function to set token URI
	@param _owner The address that owns the token
	@param _index The token index for the address
	@param _tokenURI The token URI
	"""
	self.ownerToIdToURI[_owner][_index] = _tokenURI


@internal
def _mint(_to: address, _issuer: address, _tokenURI: String[64]):
	"""
	@dev Internal function to mint tokens
	@param _to The address that will receive the minted token.
	@param _issuer The address that is issuing the token
	@param _tokenURI The token URI
	"""
	if _issuer != self.owner:
		self.operatorToRecipientToValidity[_issuer][_to] = False

	_current_token_id: uint256 = self.ownerToBalance[_to] + 1
	self.ownerToBalance[_to] = _current_token_id
	self.ownerToIdToValidity[_to][_current_token_id] = True
	self.ownerToIdToIssuer[_to][_current_token_id] = _issuer
	self.totalSupply += 1
	self._setTokenURI(_to, _current_token_id, _tokenURI)

	log Mint(_to, _current_token_id, _issuer)


@internal
def _invalidate(_owner: address, _index: uint256):
	"""
	@dev Internal function to invalidate a token for an address
	@param _owner The address which token is to be invalidated
	@param _index The token ID of the address to be invalidated
	"""
	self.ownerToIdToValidity[_owner][_index] = False

	log Invalidate(_owner, _index)


@internal
def _delegate(_operator: address, _recipient: address):
	"""
	@notice Internal function to grant one-time minting right to `operator` for `owner`
					An allowed operator can call the function to mint a token.
	@dev Throws if `_recipient` is ZERO_ADDRESS.
	@param _operator The address that will be allowed to mint a token
	@param _recipient Address for whom `operator` is allowed to mint a token
	"""
	# Throws if owner is ZERO_ADDRESS
	assert _recipient != ZERO_ADDRESS, "Invalid recipient address"

	self.operatorToRecipientToValidity[_operator][_recipient] = True

	log Delegate(_operator, _recipient)

### Internal view functions


@view
@internal
def _supportsInterface(_interfaceID: Bytes[4]) -> bool:
	"""
	@dev Internal function to check if interface is supported
	@param _interfaceID Id of the interface in Bytes[4]
	@return A boolean that indicates if the interface is supported
	"""
	return _interfaceID == ERC165_INTERFACE_ID or \
	 	_interfaceID == EIP_4671_INTERFACE_ID or \
		_interfaceID == EIP_4671_METADATA_INTERFACE_ID or \
		_interfaceID == EIP_4671_DELEGATE_INTERFACE_ID


### External functions


@external
def delegate(operator: address, recipient: address) -> bool:
	"""
	@notice Grant one-time minting right to `operator` for `owner`
  			  An allowed operator can call the function to mint a token.
	@dev Throws if `msg.sender` is not the owner of the contract
			 Throws if `operator` is ZERO_ADDRESS
	@param operator The address that will be allowed to mint a token
	@param recipient Address for whom `operator` is allowed to mint a token
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if owner is not the sender
	assert msg.sender == self.owner, "Only owner is authorised to delegate"

	# Throws if operator or owner is ZERO_ADDRESS
	assert operator != ZERO_ADDRESS, "Invalid operator address"

	self._delegate(operator, recipient)
	return True


@external
def delegateBatch(operators: DynArray[address, BATCH_SIZE], recipients: DynArray[address, BATCH_SIZE]) -> bool:
	"""
	@notice Grant one-time minting right to a list of `operators` for a corresponding list of `owners`
					An allowed operator can call the function to mint a token.
	@dev Throws if `msg.sender` is not the owner of the contract
	@param operators Addresses that will be allowed to mint a token
	@param recipients Addresses for whom `operators` are allowed to mint a token
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if owner is not the sender
	assert msg.sender == self.owner, "Only owner is authorised to delegate"

	for i in range(BATCH_SIZE):
		_operator: address = operators[i]

		# Terminate early if operator is ZERO_ADDRESS
		if _operator == ZERO_ADDRESS:
			break
		self._delegate(operators[i], recipients[i])

	return True


@external
def invalidate(owner: address, index: uint256) -> bool:
	"""
	@notice Invalidate a token for an address
	@dev Throws if `msg.sender` is not the owner of the contract
			 Throws if the index is greater than the balance of the address
	@param owner The address which token is to be invalidated
	@param index The token ID of the address to be invalidated
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if owner is not the sender
	assert msg.sender == self.owner, "Only owner is authorised to invalidate"

	# Throws if index does not exist
	assert index <= self.ownerToBalance[owner], "Index does not exist for address"

	self._invalidate(owner, index)
	return True


@external
def mint(recipient: address, tokenURI: String[64]) -> bool:
	"""
	@notice Issue a new token to an address
	@dev External function to mint a token.
			 Throws if `recipient` is ZERO_ADDRESS.
			 Throws if `msg.sender` is not the owner of the contract
	@param recipient The address that will receive the minted token
	@param tokenURI The token URI
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if `msg.sender` does not have permission to mint
	assert (msg.sender == self.owner or \
		self.operatorToRecipientToValidity[msg.sender][recipient] == True
	), "Address is not authorised to mint"
	# Throws if `_to` is zero address
	assert recipient != ZERO_ADDRESS, "Invalid address"

	self._mint(recipient, msg.sender, tokenURI)
	return True


@external
def mintBatch(recipients: DynArray[address, BATCH_SIZE], tokenURIs: DynArray[String[64], BATCH_SIZE]) -> bool:
	"""
	@notice Mint tokens to multiple addresses. Caller must have the right to mint for all owners.
	@dev External function to mint tokens in batches.
			 Throws if any of `recipients` is ZERO_ADDRESS.
			 Throws if `msg.sender` is not the owner of the contract
	@param recipients The addresses that will receive the minted token
	@param tokenURIs The token URIs
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if `msg.sender` does not have permission to mint

	for i in range(BATCH_SIZE):
		_recipient: address = recipients[i]

		# Terminate early if recipient is ZERO_ADDRESS
		if _recipient == ZERO_ADDRESS:
			break

		assert (msg.sender == self.owner or \
			self.operatorToRecipientToValidity[msg.sender][_recipient] == True
		), "Address is not authorised to mint"

		self._mint(_recipient, msg.sender, tokenURIs[i])

	return True


@view
@external
def supportsInterface(_interfaceID: bytes32) -> bool:
    """
    @dev Interface identification is specified in ERC-165.
    @param _interfaceID Id of the interface
	@return A boolean that indicates if the interface is supported.
    """
    return self._supportsInterface(slice(_interfaceID, 28, 4))


### External view functions


@external
@view
def balanceOf(owner: address) -> uint256:
	"""
	@notice Count all tokens assigned to an owner
	@param owner Address for whom to query the balance
	@return Number of tokens owned by `owner`
	"""
	return self.ownerToBalance[owner]


@external
@view
def hasValidToken(owner: address) -> bool:
	"""
	@notice Check if a given address owns a valid token
	@param owner Address to check for
	@return A boolean that indicates if the owner has a valid token
	"""
	_owner_balance: uint256 = self.ownerToBalance[owner]

	for i in range(MAX_BALANCE):
		if self.ownerToIdToValidity[owner][i] == True:
			return True

	return False


@external
@view
def issuerOf(owner: address, index: uint256) -> address:
	"""
	@notice Get the issuer of a token
	@dev Throws if the index is greater than the balance of the address
	@param owner Address for whom to check the token issuer
	@param index Index of the token
	@return Address of the issuer
	"""
	assert index <= self.ownerToBalance[owner], "Index does not exist for address"

	return self.ownerToIdToIssuer[owner][index]


@external
@view
def isValid(owner: address, index: uint256) -> bool:
	"""
	@notice Check if a token hasn't been invalidated
	@dev Throws if the index is greater than the balance of the address
	@param owner Address for whom to check the token validity
	@param index Index of the token
	@return True if the token is valid, False otherwise
	"""
	assert index <= self.ownerToBalance[owner], "Index does not exist for address"

	return self.ownerToIdToValidity[owner][index]


@external
@view
def tokenURI(owner: address, index: uint256) -> String[128]:
	"""
	@notice URI to query to get the token's metadata
	@dev Throws if the index is greater than the balance of the address
	@param owner Address of the token's owner
	@param index Index of the token
	@return URI for the token
	"""
	assert index <= self.ownerToBalance[owner], "Index does not exist for address"

	return concat(
		self.baseTokenURI,
		self.ownerToIdToURI[owner][index]
	)


@external
@view
def canMint(operator: address, recipient: address) -> bool:
	"""
	@notice Check if an address has permission to mint for another address
	@param operator The address of the intended minter
	@param recipient The address of the intended recipient
	@return Boolean value indicating if operator address has permission to mint
					to the recipient
	"""
	return self.operatorToRecipientToValidity[operator][recipient] == True

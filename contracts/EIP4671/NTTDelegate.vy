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
	tokenId: uint256
	issuer: indexed(address)


event Invalidate:
	owner: indexed(address)
	tokenId: uint256


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
totalSupply: uint256

# @dev Mapping from token ID to validity
tokenIdToValidity: HashMap[uint256, bool]

# @dev Mapping from token ID to issuer
tokenIdToIssuer: HashMap[uint256, address]

# @dev Mapping from address to token index for an address to token ID
ownerToIndexToId: HashMap[address, HashMap[uint256, uint256]]

# @dev Mapping from token ID to owner
tokenIdToOwner: HashMap[uint256, address]

# @dev Mapping from address to balance
ownerToBalance: HashMap[address, uint256]

# @dev Mapping from token ID to URI
tokenIdToURI: HashMap[uint256, String[64]]

# @dev Mapping from deleagted operator address to recipient address to
# 		 delegation validity
operatorToRecipientToValidity: HashMap[address, HashMap[address, bool]]

# @dev ERC165 interface ID of ERC165
ERC165_INTERFACE_ID: constant(Bytes[32]) = b"\x01\xff\xc9\xa7"

# @dev ERC165 interface ID of EIP4671
EIP_4671_INTERFACE_ID: constant(Bytes[32]) = b"\xa5\x11S="

# @dev ERC165 interface ID of EIP4671Metadata
EIP_4671_METADATA_INTERFACE_ID: constant(Bytes[32]) = b"[^\x13\x9f"

# @dev ERC165 interface ID of EIP4671Enumerable
EIP_4671_ENUMERABLE_INTERFACE_ID: constant(Bytes[32]) = b"\x02\xaf\x8dc"

# @dev ERC165 interface ID of EIP4671 Delegate
EIP_4671_DELEGATE_INTERFACE_ID: constant(Bytes[32]) = b"y){&"

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
def _setTokenURI(_tokenId: uint256, _tokenURI: String[64]):
	"""
	@dev Internal function to set token URI
	@param _tokenId The token ID
	@param _tokenURI The token URI
	"""
	self.tokenIdToURI[_tokenId] = _tokenURI


@internal
def _mint(_to: address, _issuer: address):
	"""
	@dev Internal function to mint tokens
	@param _to The address that will receive the minted token.
	@param _issuer The address that is issuing the token
	@param _tokenURI The token URI
	"""
	if _issuer != self.owner:
		self.operatorToRecipientToValidity[_issuer][_to] = False

	_current_token_id: uint256 = self.totalSupply + 1
	self.totalSupply = _current_token_id
	self.tokenIdToValidity[_current_token_id] = True
	self.tokenIdToIssuer[_current_token_id] = _issuer
	self.tokenIdToOwner[_current_token_id] = _to

	_current_owner_index: uint256 = self.ownerToBalance[_to]
	self.ownerToBalance[_to] = _current_owner_index
	self.ownerToIndexToId[_to][_current_owner_index] = _current_token_id
	self.ownerToBalance[_to] = _current_owner_index + 1

	log Mint(_to, _current_token_id, _issuer)


@internal
def _invalidate(_tokenId: uint256):
	"""
	@dev Internal function to invalidate a token for an address
	@param _tokenId The token ID to be invalidated
	"""
	self.tokenIdToValidity[_tokenId] = False
	_owner: address = self.tokenIdToOwner[_tokenId]

	log Invalidate(_owner, _tokenId)


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
		_interfaceID == EIP_4671_DELEGATE_INTERFACE_ID or \
		_interfaceID == EIP_4671_ENUMERABLE_INTERFACE_ID


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
def invalidate(tokenId: uint256) -> bool:
	"""
	@notice Invalidate a token for an address
	@dev Throws if `msg.sender` is not the owner of the contract
		 Throws if the token ID is greater than the total supply
	@param tokenId The token ID to be invalidated
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if owner is not the sender
	assert msg.sender == self.owner, "Only owner is authorised to invalidate"

	# Throws if token ID does not exist
	assert tokenId <= self.totalSupply, "Token ID does not exist"

	self._invalidate(tokenId)
	return True


@external
def mint(recipient: address) -> bool:
	"""
	@notice Issue a new token to an address
	@dev External function to mint a token.
		 Throws if `recipient` is ZERO_ADDRESS.
		 Throws if `msg.sender` is not the owner of the contract
	@param recipient The address that will receive the minted token
	@return A boolean that indicates if the operation was successful.
	"""
	# Throws if `msg.sender` does not have permission to mint
	assert (msg.sender == self.owner or \
		self.operatorToRecipientToValidity[msg.sender][recipient] == True
	), "Address is not authorised to mint"
	# Throws if `_to` is zero address
	assert recipient != ZERO_ADDRESS, "Invalid address"

	self._mint(recipient, msg.sender)
	_current_token_id: uint256 = self.totalSupply

	return True


@external
def mintBatch(recipients: DynArray[address, BATCH_SIZE]) -> bool:
	"""
	@notice Mint tokens to multiple addresses. Caller must have the right to mint for all owners.
	@dev External function to mint tokens in batches.
			 Throws if any of `recipients` is ZERO_ADDRESS.
			 Throws if `msg.sender` is not the owner of the contract
	@param recipients The addresses that will receive the minted token
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

		self._mint(_recipient, msg.sender)

	return True


@external
def setTokenURI(tokenId: uint256, tokenURI: String[64]):
	"""
	@notice Set the token URI for a token ID
	@param tokenId Token ID to set URI for
	@param tokenURI URI to set
	"""
	assert tokenId <= self.totalSupply, "Token ID does not exist"

	self._setTokenURI(tokenId, tokenURI)


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
def ownerOf(tokenId: uint256) -> address:
	"""
	@notice Get the owner of a token
	@param tokenId The token ID to check for
	@return Address that owns the token ID
	"""
	assert tokenId <= self.totalSupply, "Token ID does not exist"
	return self.tokenIdToOwner[tokenId]


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
		_tokenId: uint256 = self.ownerToIndexToId[owner][i]
		if self.tokenIdToValidity[_tokenId] == True:
			return True

	return False


@external
@view
def issuerOf(tokenId: uint256) -> address:
	"""
	@notice Get the issuer of a token
	@dev Throws if the token ID is greater than the total supply
	@param tokenId Token ID
	@return Address of the issuer
	"""
	assert tokenId <= self.totalSupply, "Token ID does not exist"

	return self.tokenIdToIssuer[tokenId]


@external
@view
def isValid(tokenId: uint256) -> bool:
	"""
	@notice Check if a token hasn't been invalidated
	@dev Throws if the token ID is greater than the total supply
	@param tokenId Token ID
	@return True if the token is valid, False otherwise
	"""
	assert tokenId <= self.totalSupply, "Token ID does not exist"

	return self.tokenIdToValidity[tokenId]


@external
@view
def tokenURI(tokenId: uint256) -> String[128]:
	"""
	@notice URI to query to get the token's metadata
	@dev Throws if the token ID is greater than the total supply
	@param tokenId Token ID
	@return URI for the token
	"""
	assert tokenId <= self.totalSupply, "Token ID does not exist"

	return concat(
		self.baseTokenURI,
		self.tokenIdToURI[tokenId]
	)


@external
@view
def tokenOfOwnerByIndex(owner: address, index: uint256) -> uint256:
	"""
	@notice Get the token ID of a token based on its position in the owner's index
	@dev Throws if `index` is greater than the balance for `owner`
	@param owner Address for whom to get the token
	@param index Index of the address
	@return Token ID
	"""
	assert index < self.ownerToBalance[owner], "Index does not exist for address"

	_tokenId: uint256 = self.ownerToIndexToId[owner][index]

	assert _tokenId != 0, "Address does not have any tokens"

	return _tokenId


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


@external
@view
def total() -> uint256:
	"""
	@notice Get the total number of tokens minted
	@return Total number of tokens minted
	"""
	return self.totalSupply

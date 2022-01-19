# @version ^0.3.0

# @dev Name of the token
name: public(String[64])

# @dev Abbreviated name of the token
symbol: public(String[32])

@external
@view
def balanceOf(owner: address) -> uint256:
	"""
	@notice Count all tokens assigned to an owner
	@param owner Address for whom to query the balance
	@return Number of tokens owned by `owner`
	"""
	pass


@external
@view
def isValid(owner: address, index: uint256) -> bool:
	"""
	@notice Check if a token hasn't been invalidated
	@param owner Address for whom to check the token validity
	@param index Index of the token
	@return True if the token is valid, False otherwise
	"""
	pass


@external
@view
def issuerOf(owner: address, index: uint256) -> address:
	"""
	@notice Get the issuer of a token
	@param owner Address for whom to check the token issuer
	@param owner Index of the token
	@return Address of the issuer
	"""
	pass


@external
@view
def tokenURI(owner: address, index: uint256) -> String[128]:
	"""
	@notice URI to query to get the token's metadata
	@param owner Address of the token's owner
	@param index Index of the token
	@return URI for the token
	"""
	pass

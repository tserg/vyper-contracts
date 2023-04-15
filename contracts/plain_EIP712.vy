# @version ^0.3.0

"""
@title Contract to sign and verify EIP-712 messages.
@license GPL-3.0
@author Gary Tse
@notice You can use this contract to see how EIP-712 messages can be implemented
		in Vyper.
"""

event Incoming:
	sms: uint256
	sender: indexed(address)

DOMAIN_SEPARATOR: public(immutable(bytes32))
DOMAIN_TYPE_HASH: public(constant(bytes32)) = keccak256(
	"EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
)
PERMIT_TYPE_HASH: public(constant(bytes32)) = keccak256(
	"Message(uint256 sms)"
)

@external
def __init__():
	DOMAIN_SEPARATOR = keccak256(
		_abi_encode(
			DOMAIN_TYPE_HASH,
			keccak256(convert("Plain", Bytes[5])),
			keccak256(convert("1.0.0", Bytes[5])),
			convert(chain.id, bytes32),
			self,
		)
	)

@external
def message(
	sms: uint256,
	signature: Bytes[65]
) -> bool:
	"""
	@notice Verify a signature and check if it was signed by `msg.sender`.
	@dev Throws if the signature cannot be verified.
	@param sms An arbitrary number to append to the message
	@param signature A 65-bytes signature comprising v, r and s components.
	@return True if the signature is verified.
	"""
	digest: bytes32 = keccak256(
		concat(
			b"\x19\x01",
			DOMAIN_SEPARATOR,
			keccak256(
				_abi_encode(
					PERMIT_TYPE_HASH,
					sms,
				)
			)
		)
	)

	r: uint256 = convert(slice(signature, 0, 32), uint256)
	s: uint256 = convert(slice(signature, 32, 32), uint256)
	v: uint256 = convert(slice(signature, 64, 1), uint256)

	assert ecrecover(digest, v, r, s) == msg.sender
	log Incoming(sms, msg.sender)
	return True

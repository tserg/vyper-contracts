# @version ^0.3.0

event Incoming:
	sms: uint256
	sender: indexed(address)

CHAIN_ID: immutable(uint256)

DOMAIN_SEPARATOR: public(bytes32)
DOMAIN_TYPE_HASH: constant(bytes32) = keccak256(
	'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)'
)
PERMIT_TYPE_HASH: constant(bytes32) = keccak256(
	"Message(uint256 sms)"
)

@external
def __init__():
	_chain_id: uint256 = chain.id
	CHAIN_ID = _chain_id
	self.DOMAIN_SEPARATOR = keccak256(
		concat( # not sure why _abi_encode does not work
			DOMAIN_TYPE_HASH,
			keccak256(convert("Plain", Bytes[5])),
			keccak256(convert("1.0.0", Bytes[5])),
			convert(1337, bytes32), # not sure why chain.id or _chain_id does not work
			convert(self, bytes32),
		)
	)

@external
def message(
	sms: uint256,
	signature: Bytes[65]
) -> bool:

	digest: bytes32 = keccak256(
		concat(
			b'\x19\x01',
			self.DOMAIN_SEPARATOR,
			keccak256(
				concat(
					PERMIT_TYPE_HASH,
					convert(CHAIN_ID, bytes32)
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

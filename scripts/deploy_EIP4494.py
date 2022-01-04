from brownie import (
    accounts,
    chain,
    EIP4494
)

from eip712.messages import EIP712Message

def main():

    c = accounts[0].deploy(
        EIP4494,
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        accounts[0],
        accounts[0]
    )

    local = accounts.add()
    accounts[0].transfer(local, 50000)

    c.mint(
        local,
        '1.json',
        {'from': accounts[0]}
    )

    assert c.ownerOf(1) == local

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "0.0.1"
        _chainId_: "uint256" = chain.id
        _verifyingContract_: "address" = c.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(c.nonces(1))
    deadline = int(chain.time() + 100000)

    permit = Permit(
        spender=accounts[1].address,
        tokenId=1,
        nonce=nonce,
        deadline=deadline
    )

    signed = local.sign_message(permit)
    signed_message_hex = signed.messageHash.hex()


    tx = c.permit(
        permit.spender,
        permit.tokenId,
        permit.deadline,
        signed_message_hex,
        {'from': local}
    )

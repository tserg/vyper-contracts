from brownie import (
    accounts,
    chain,
    PlainEIP712
)

from eip712.messages import EIP712Message

def main():

    c = PlainEIP712.deploy({'from': accounts[0]})

    local_account = accounts.add()

    class Message(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Plain"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = chain.id
        _verifyingContract_: "address" = c.address

        sms: "uint256"

    permit = Message(sms=1)

    signed = local_account.sign_message(permit)
    print(signed.signature)

    tx = c.message(
        1,
        signed.signature,
        {'from': local_account}
    )

    print(tx.events)

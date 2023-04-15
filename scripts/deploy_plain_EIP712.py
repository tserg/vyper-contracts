from ape import (
    accounts,
    chain,
    project,
    networks,
)

from eip712.messages import EIP712Message

def main():
    deployer = accounts.test_accounts[0]

    c = project.plain_EIP712.deploy(sender=deployer)

    local_account = accounts.test_accounts[1]

    chain_id = networks.provider.chain_id
    print("chain_id: ", chain_id)
    class Message(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Plain"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = chain_id
        _verifyingContract_: "address" = c.address

        sms: "uint256"

    permit = Message(sms=12)

    signed = local_account.sign_message(permit)
    print(signed)

    tx = c.message(
        12,
        signed.encode_rsv(),
        sender=local_account,
    )

    print(tx.events)

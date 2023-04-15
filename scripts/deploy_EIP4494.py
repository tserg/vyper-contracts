from ape import (
    accounts,
    chain,
    project,
    networks,
)

from eip712.messages import EIP712Message

def main():
    print(networks.provider.name)
    deployer = accounts.test_accounts[0]

    c = project.EIP4494.deploy(
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        deployer,
        deployer,
        sender=deployer,
    )

    local_account = accounts.test_accounts[1]
    deployer.transfer(local_account, 50000)

    c.mint(
        local_account,
        '1.json',
        sender=deployer
    )

    assert c.ownerOf(1) == local_account

    chain_id = networks.provider.chain_id
    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = chain_id
        _verifyingContract_: "address" = c.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(c.nonces(1))
    deadline = int(chain.blocks.head.timestamp + 100000)

    permit = Permit(
        spender=local_account.address,
        tokenId=1,
        nonce=nonce,
        deadline=deadline
    )

    signed = local_account.sign_message(permit)
    print(signed)

    tx = c.permit(
        permit.spender,
        permit.tokenId,
        permit.deadline,
        signed.encode_rsv(),
        sender=local_account,
    )

    print(tx.events)

from brownie import (
    accounts,
    chain,
    ERC20,
    Bridge,
)

STARKNET_CORE_GOERLI_ADDRESS = "0xde29d060D45901Fb19ED6C6e959EB22d8626708e"

# Use Goerli testnet

def main():

    a1 = accounts.load("deployment_account")

    # Deploy the ERC20

    token = ERC20.deploy(
        "Starknet Token",
        "STNT",
        18,
        10000000,
        {'from': a1}
    )

    # Deploy the bridge

    bridge = Bridge.deploy(
        token.address,
        STARKNET_CORE_GOERLI_ADDRESS,
        {'from': a1}
    )

    # Approve tokens for the bridge

    token.approve(bridge.address, 10000000, {'from': a1})

    # Compile Starknet contract with bridge contract address updated, and deploy

    # starknet-compile l1l2.cairo --output l1l2_compiled.json --abi l1l2_abi.json
    # starknet deploy --contract l1l2_compiled.json

    # Call deposit on L1 contract

    # Check balance on L2 contract

    # starknet call --address L2_CONTRACT_ADDRESS --abi l1l2_abi.json --function get_balance --inputs ADDRESS

    # Call withdraw on L2 contract

    # starknet invoke --address L2_CONTRACT_ADDRESS --abi l1l2_abi.json --function withdraw --inputs L2_ADDRESS L1_ADDRESS AMOUNT

    # Call withdraw on L1 contract

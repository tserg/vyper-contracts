from ape import (
    accounts,
    chain,
    project,
)

def main():
    deployer = accounts.test_accounts[0]

    erc721 = project.timer.deploy(
        "Time Token",
        "TT",
        "https://www.test.com/",
        100,
        deployer,
        deployer,
        sender=deployer,
    )

    erc20 = project.ERC20_mintable.deploy(
        "Mineable Token",
        "MNT",
        18,
        0,
        erc721.address,
        sender=deployer,
    )

    erc721.set_token_address(erc20.address, sender=deployer)

    

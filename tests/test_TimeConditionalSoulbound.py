import pytest

from brownie import (
    reverts,
    ZERO_ADDRESS
)

@pytest.fixture(scope="module", autouse=True)
def erc721(accounts, TimedERC721):
    c = accounts[0].deploy(
        TimedERC721,
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        accounts[0],
        accounts[0]
    )

    # Mint 1 token
    c.mint(
        accounts[0],
        '1.json',
        {'from': accounts[0]}
    )
    yield c


@pytest.fixture(scope="module", autouse="True")
def tcs(accounts, erc721, TimeConditionalSoulbound):
    c = accounts[0].deploy(
        TimeConditionalSoulbound,
        "Non-Tradable Token",
        "TCS",
        "https://tcs.com",
        100,
        erc721.address,
        1000,
    )
    yield c


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_start_state(erc721, tcs):

    assert tcs.token() == erc721.address
    assert tcs.minimumTime() == 1000


def test_invalid_mint(accounts, erc721, tcs):

    with reverts("Timed ERC-721 conditions not met"):
        tcs.mint(
            accounts[0],
            "/1.json",
            {'from': accounts[0]},
        )


def test_valid_mint(accounts, chain, erc721, tcs):

    chain.sleep(1001)

    tx = tcs.mint(
        accounts[0],
        "/1.json",
        {'from': accounts[0]},
    )

    assert len(tx.events) == 1
    assert tx.events[0]["owner"] == accounts[0]
    assert tx.events[0]["tokenId"] == 1

    assert tcs.total() == 1
    assert tcs.ownerOf(1) == accounts[0]
    assert tcs.balanceOf(accounts[0]) == 1
    assert tcs.tokenOfOwnerByIndex(accounts[0], 0) == 1
    assert tcs.tokenURI(1) == "https://tcs.com/1.json"

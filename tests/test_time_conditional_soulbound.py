import pytest
from ape import reverts


@pytest.fixture(scope="class", autouse=True)
def erc721(accounts, project):
    c = project.timed_ERC721.deploy(
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        accounts[0],
        accounts[0],
        sender=accounts[0],
    )

    # Mint 1 token
    c.mint(accounts[0], "1.json", sender=accounts[0])
    yield c


@pytest.fixture(scope="class", autouse="True")
def tcs(accounts, project, erc721):
    c = project.time_conditional_soulbound.deploy(
        "Non-Tradable Token",
        "TCS",
        "https://tcs.com",
        100,
        erc721.address,
        1000,
        sender=accounts[0],
    )
    yield c


def test_start_state(erc721, tcs):

    assert tcs.token() == erc721.address
    assert tcs.minimumTime() == 1000


def test_invalid_mint(accounts, erc721, tcs):

    with reverts("Timed ERC-721 conditions not met"):
        tcs.mint(accounts[0], "/1.json", sender=accounts[0])


def test_valid_mint(accounts, chain, erc721, tcs):

    chain.mine(1001)

    tx = tcs.mint(accounts[0], "/1.json", sender=accounts[0])

    events = list(tx.decode_logs(tcs.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[0]
    assert events[0].event_arguments["tokenId"] == 1

    assert tcs.total() == 1
    assert tcs.ownerOf(1) == accounts[0]
    assert tcs.balanceOf(accounts[0]) == 1
    assert tcs.tokenOfOwnerByIndex(accounts[0], 0) == 1
    assert tcs.tokenURI(1) == "https://tcs.com/1.json"

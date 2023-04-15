import pytest
from ape import reverts

from tests.constants import (
    ERC165_INTERFACE_ID,
    ERC721_ENUMERABLE_INTERFACE_ID,
    ERC721_INTERFACE_ID,
    ERC721_METADATA_INTERFACE_ID,
    ERC721_TOKEN_RECEIVER_INTERFACE_ID,
    INVALID_INTERFACE_ID,
    ZERO_ADDRESS,
)

# Tests adapted from official Vyper example


@pytest.fixture(scope="class", autouse=True)
def erc721(accounts, project):
    c = project.ERC721.deploy(
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


def test_supportsInterface(erc721):

    assert erc721.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert erc721.supportsInterface(ERC721_INTERFACE_ID) == 1
    assert erc721.supportsInterface(ERC721_METADATA_INTERFACE_ID) == 1
    assert erc721.supportsInterface(ERC721_ENUMERABLE_INTERFACE_ID) == 1
    assert erc721.supportsInterface(ERC721_TOKEN_RECEIVER_INTERFACE_ID) == 1

    assert erc721.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_name(erc721):

    assert erc721.name() == "Test Token"


def test_symbol(erc721):

    assert erc721.symbol() == "TST"


def test_totalSupply(erc721):

    assert erc721.totalSupply() == 1


def test_baseURI(erc721):

    assert erc721.baseURI() == "https://www.test.com/"


def test_tokenURI(erc721):

    assert erc721.tokenURI(1) == "https://www.test.com/1.json"

    with reverts():
        erc721.tokenURI(0)


def test_balanceOf(accounts, erc721):

    assert erc721.balanceOf(accounts[0]) == 1
    assert erc721.balanceOf(accounts[1]) == 0


def test_ownerOf(accounts, erc721):

    assert erc721.ownerOf(1) == accounts[0]

    with reverts():
        erc721.ownerOf(2)


def test_tokenByIndex(erc721):

    assert erc721.tokenByIndex(1) == 1


def test_tokenOfOwnerByIndex(erc721, accounts):

    assert erc721.tokenOfOwnerByIndex(accounts[0], 1) == 1


def test_getApproved(accounts, erc721):

    assert erc721.getApproved(1) == ZERO_ADDRESS

    erc721.approve(accounts[1], 1, sender=accounts[0])
    assert erc721.getApproved(1) == accounts[1]


def test_isApprovedForAll(erc721, accounts):

    assert erc721.isApprovedForAll(accounts[0], accounts[1]) == 0

    erc721.setApprovalForAll(accounts[1], True, sender=accounts[0])
    assert erc721.isApprovedForAll(accounts[0], accounts[1]) == 1


def test_transferFrom_by_owner(accounts, erc721):

    with reverts():
        erc721.transferFrom(ZERO_ADDRESS, accounts[0], 1, sender=accounts[1])

        erc721.transferFrom(accounts[0], accounts[1], 1, sender=accounts[1])

        erc721.transferFrom(accounts[0], accounts[1], 2, sender=accounts[0])

    tx = erc721.transferFrom(accounts[0], accounts[1], 1, sender=accounts[0])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[1]) == 1

    assert erc721.ownerOf(1) == accounts[1]


def test_transferFrom_by_approved(accounts, erc721):

    erc721.approve(accounts[1], 1, sender=accounts[0])
    tx = erc721.transferFrom(accounts[0], accounts[2], 1, sender=accounts[1])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_transferFrom_by_operator(accounts, erc721):

    erc721.setApprovalForAll(accounts[1], True, sender=accounts[0])
    tx = erc721.transferFrom(accounts[0], accounts[2], 1, sender=accounts[1])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_safeTransferFrom_by_owner(accounts, erc721):

    with reverts():
        erc721.safeTransferFrom(ZERO_ADDRESS, accounts[0], 1, sender=accounts[1])

        erc721.safeTransferFrom(accounts[0], accounts[1], 1, sender=accounts[1])

        erc721.safeTransferFrom(accounts[0], accounts[1], 2, sender=accounts[0])

    tx = erc721.safeTransferFrom(accounts[0], accounts[1], 1, sender=accounts[0])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[1]) == 1

    assert erc721.ownerOf(1) == accounts[1]


def test_safeTransferFrom_by_approved(accounts, erc721):

    erc721.approve(accounts[1], 1, sender=accounts[0])
    tx = erc721.safeTransferFrom(accounts[0], accounts[2], 1, sender=accounts[1])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_safeTransferFrom_by_operator(accounts, erc721):

    erc721.setApprovalForAll(accounts[1], True, sender=accounts[0])
    tx = erc721.safeTransferFrom(accounts[0], accounts[2], 1, sender=accounts[1])

    events = list(tx.decode_logs(erc721.Transfer))
    assert len(events) == 1
    assert events[0].event_arguments["sender"] == accounts[0]
    assert events[0].event_arguments["receiver"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_burn(accounts, erc721):

    with reverts():
        # No ownership
        erc721.burn(1, sender=accounts[1])

    erc721.burn(1, sender=accounts[0])

    assert erc721.totalSupply() == 0
    assert erc721.balanceOf(accounts[0]) == 0

    with reverts():
        assert erc721.ownerOf(1) == ZERO_ADDRESS

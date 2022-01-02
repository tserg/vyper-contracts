import pytest

from brownie import (
    reverts,
    ZERO_ADDRESS,
)


ERC165_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
ERC721_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000080ac58cd"
INVALID_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000012345678"
ERC721_METADATA_INTERFACE_ID = b'[^\x13\x9f'
ERC721_ENUMERABLE_INTERFACE_ID = b'x\x0e\x9dc'
ERC721_TOKEN_RECEIVER_INTERFACE_ID = b'\x15\x0bz\x02'


# Tests adapted from official Vyper example


@pytest.fixture(scope="module", autouse="True")
def erc721(accounts, ERC721):
    c = accounts[0].deploy(
        ERC721,
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


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


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

    erc721.approve(accounts[1], 1, {'from': accounts[0]})
    assert erc721.getApproved(1) == accounts[1]


def test_isApprovedForAll(erc721, accounts):

    assert erc721.isApprovedForAll(accounts[0], accounts[1]) == 0

    erc721.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    assert erc721.isApprovedForAll(accounts[0], accounts[1]) == 1


def test_transferFrom_by_owner(accounts,erc721):

    with reverts():
        erc721.transferFrom(
            ZERO_ADDRESS,
            accounts[0],
            1,
            {'from': accounts[1]}
        )

        erc721.transferFrom(
            accounts[0],
            accounts[1],
            1,
            {'from': accounts[1]}
        )

        erc721.transferFrom(
            accounts[0],
            accounts[1],
            2,
            {'from': accounts[0]}
        )

    tx = erc721.transferFrom(
        accounts[0],
        accounts[1],
        1,
        {'from': accounts[0]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[1]) == 1

    assert erc721.ownerOf(1) == accounts[1]


def test_transferFrom_by_approved(accounts, erc721):

    erc721.approve(accounts[1], 1, {'from': accounts[0]})
    tx = erc721.transferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_transferFrom_by_operator(accounts, erc721):

    erc721.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    tx = erc721.transferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_safeTransferFrom_by_owner(accounts,erc721):

    with reverts():
        erc721.safeTransferFrom(
            ZERO_ADDRESS,
            accounts[0],
            1,
            {'from': accounts[1]}
        )

        erc721.safeTransferFrom(
            accounts[0],
            accounts[1],
            1,
            {'from': accounts[1]}
        )

        erc721.safeTransferFrom(
            accounts[0],
            accounts[1],
            2,
            {'from': accounts[0]}
        )

    tx = erc721.safeTransferFrom(
        accounts[0],
        accounts[1],
        1,
        {'from': accounts[0]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[1]) == 1

    assert erc721.ownerOf(1) == accounts[1]


def test_safeTransferFrom_by_approved(accounts, erc721):

    erc721.approve(accounts[1], 1, {'from': accounts[0]})
    tx = erc721.safeTransferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_safeTransferFrom_by_operator(accounts, erc721):

    erc721.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    tx = erc721.safeTransferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert erc721.balanceOf(accounts[0]) == 0
    assert erc721.balanceOf(accounts[2]) == 1

    assert erc721.ownerOf(1) == accounts[2]


def test_burn(accounts, erc721):

    with reverts():
        # No ownership
        erc721.burn(1, {'from': accounts[1]})

    erc721.burn(1, {'from': accounts[0]})

    assert erc721.totalSupply() == 0
    assert erc721.balanceOf(accounts[0]) == 0

    with reverts():
        assert erc721.ownerOf(1) == ZERO_ADDRESS

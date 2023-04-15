import pytest
from ape import reverts

from tests.constants import (
    EIP_4671_ENUMERABLE_INTERFACE_ID,
    EIP_4671_INTERFACE_ID,
    EIP_4671_METADATA_INTERFACE_ID,
    ERC165_INTERFACE_ID,
    INVALID_INTERFACE_ID,
    ZERO_ADDRESS,
)


@pytest.fixture(scope="class", autouse="True")
def ntt(accounts, project):
    c = project.NTT.deploy(
        "Non-Tradable Token", "NTT", "https://ntt.com", 100, sender=accounts[0]
    )
    yield c


@pytest.fixture
def mint_a1_1(accounts, ntt):
    tx = ntt.mint(accounts[1], "/1.json", sender=accounts[0])
    yield tx


@pytest.fixture
def mint_a1_2(accounts, ntt):
    tx = ntt.mint(accounts[1], "/2.json", sender=accounts[0])
    yield tx


@pytest.fixture
def invalidate_a1_1(accounts, ntt):
    tx = ntt.invalidate(1, sender=accounts[0])
    yield tx


def test_start_state(ntt):

    assert ntt.name() == "Non-Tradable Token"
    assert ntt.symbol() == "NTT"
    assert ntt.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_METADATA_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_ENUMERABLE_INTERFACE_ID) == 1
    assert ntt.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_mint(accounts, ntt, mint_a1_1):

    events = list(mint_a1_1.decode_logs(ntt.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[0]

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[0]
    assert ntt.isValid(1) is True
    assert ntt.ownerOf(1) == accounts[1]
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) is True
    assert ntt.tokenOfOwnerByIndex(accounts[1], 0) == 1
    assert ntt.tokenURI(1) == "https://ntt.com/1.json"


def test_mint_non_owner_fail(accounts, ntt):

    with reverts("Only owner is authorised to mint"):
        ntt.mint(accounts[2], "/forbidden.json", sender=accounts[1])


def test_mint_zero_address_fail(accounts, ntt):

    with reverts("Invalid address"):
        ntt.mint(ZERO_ADDRESS, "/forbidden.json", sender=accounts[0])


def test_invalidate(accounts, ntt, mint_a1_1, invalidate_a1_1):

    events = list(invalidate_a1_1.decode_logs(ntt.Invalidate))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[0]
    assert ntt.isValid(1) is False
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) is False


def test_mint_nonexistent_index_fail(accounts, ntt, mint_a1_1):

    with reverts("Token ID does not exist"):
        ntt.invalidate(2, sender=accounts[0])


def test_invalidate_non_owner_fail(accounts, ntt, mint_a1_1):

    with reverts("Only owner is authorised to invalidate"):
        ntt.invalidate(1, sender=accounts[2])


def test_multiple_mint_a1(accounts, ntt, mint_a1_1, mint_a1_2):

    events = list(mint_a1_2.decode_logs(ntt.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 2

    assert ntt.total() == 2
    assert ntt.issuerOf(2) == accounts[0]
    assert ntt.isValid(2) is True
    assert ntt.ownerOf(2) == accounts[1]
    assert ntt.balanceOf(accounts[1]) == 2
    assert ntt.hasValidToken(accounts[1]) is True
    assert ntt.tokenOfOwnerByIndex(accounts[1], 0) == 1
    assert ntt.tokenOfOwnerByIndex(accounts[1], 1) == 2
    assert ntt.tokenURI(2) == "https://ntt.com/2.json"

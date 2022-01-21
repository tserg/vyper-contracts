import pytest

from brownie import (
    reverts,
    ZERO_ADDRESS
)


ERC165_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
EIP_4671_INTERFACE_ID = "0x00000000000000000000000000000000000000000000000000000000d24be238"
EIP_4671_METADATA_INTERFACE_ID = "0x000000000000000000000000000000000000000000000000000000007af92637"
INVALID_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000012345678"


@pytest.fixture(scope="module", autouse="True")
def ntt(accounts, NTT):
    c = accounts[0].deploy(
        NTT,
        "Non-Tradable Token",
        "NTT",
        "https://ntt.com",
        100
    )
    yield c


@pytest.fixture
def mint_a1_1(accounts, ntt):
    tx = ntt.mint(
        accounts[1],
        "/1.json",
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def mint_a1_2(accounts, ntt):
    tx = ntt.mint(
        accounts[1],
        "/2.json",
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def invalidate_a1_1(accounts, ntt):
    tx = ntt.invalidate(
        accounts[1],
        1,
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_start_state(ntt):

    assert ntt.name() == "Non-Tradable Token"
    assert ntt.symbol() == "NTT"
    assert ntt.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_METADATA_INTERFACE_ID) == 1
    assert ntt.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_mint(accounts, ntt, mint_a1_1):

    assert len(mint_a1_1.events) == 1
    assert mint_a1_1.events[0]["owner"] == accounts[1]
    assert mint_a1_1.events[0]["index"] == 1
    assert mint_a1_1.events[0]["issuer"] == accounts[0]

    assert ntt.totalSupply() == 1
    assert ntt.issuerOf(accounts[1], 1) == accounts[0]
    assert ntt.isValid(accounts[1], 1) == True
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) == True
    assert ntt.tokenURI(accounts[1], 1) == "https://ntt.com/1.json"


def test_mint_non_owner_fail(accounts, ntt):

    with reverts("Only owner is authorised to mint"):
        ntt.mint(
            accounts[2],
            "/forbidden.json",
            {'from': accounts[1]}
        )


def test_mint_zero_address_fail(accounts, ntt):

    with reverts("Invalid address"):
        ntt.mint(
            ZERO_ADDRESS,
            "/forbidden.json",
            {'from': accounts[0]}
        )


def test_invalidate(accounts, ntt, mint_a1_1, invalidate_a1_1):

    assert len(invalidate_a1_1.events) == 1
    assert invalidate_a1_1.events[0]["owner"] == accounts[1]
    assert invalidate_a1_1.events[0]["index"] == 1

    assert ntt.totalSupply() == 1
    assert ntt.issuerOf(accounts[1], 1) == accounts[0]
    assert ntt.isValid(accounts[1], 1) == False
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) == False


def test_invalidate_non_owner_fail(accounts, ntt, mint_a1_1):

    with reverts("Only owner is authorised to invalidate"):
        ntt.invalidate(
            accounts[1],
            1,
            {'from': accounts[2]}
        )


def test_mint_nonexistent_index_fail(accounts, ntt, mint_a1_1):

    with reverts("Index does not exist for address"):
        ntt.invalidate(
            accounts[1],
            2,
            {'from': accounts[0]}
        )


def test_invalidate_non_owner_fail(accounts, ntt, mint_a1_1):

    with reverts("Only owner is authorised to invalidate"):
        ntt.invalidate(
            accounts[1],
            1,
            {'from': accounts[2]}
        )


def test_multiple_mint_a1(accounts, ntt, mint_a1_1, mint_a1_2):

    assert len(mint_a1_2.events) == 1
    assert mint_a1_2.events[0]["owner"] == accounts[1]
    assert mint_a1_2.events[0]["index"] == 2

    assert ntt.totalSupply() == 2
    assert ntt.issuerOf(accounts[1], 2) == accounts[0]
    assert ntt.isValid(accounts[1], 2) == True
    assert ntt.balanceOf(accounts[1]) == 2
    assert ntt.hasValidToken(accounts[1]) == True
    assert ntt.tokenURI(accounts[1], 2) == "https://ntt.com/2.json"
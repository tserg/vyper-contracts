import pytest

from brownie import (
    reverts,
    ZERO_ADDRESS
)


ERC165_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
EIP_4671_INTERFACE_ID = "0x00000000000000000000000000000000000000000000000000000000a511533d"
EIP_4671_METADATA_INTERFACE_ID = "0x000000000000000000000000000000000000000000000000000000005b5e139f"
EIP_4671_ENUMERABLE_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000002af8d63"
EIP_4671_DELEGATE_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000079297b26"
INVALID_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000012345678"


@pytest.fixture(scope="module", autouse="True")
def ntt(accounts, NTTDelegate):
    c = accounts[0].deploy(
        NTTDelegate,
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
        #"/1.json",
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def mint_a1_2(accounts, ntt):
    tx = ntt.mint(
        accounts[1],
        #"/2.json",
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def invalidate_a1_1(accounts, ntt):
    tx = ntt.invalidate(
        1,
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def delegate_single(accounts, ntt):
    tx = ntt.delegate(
        accounts[2],
        accounts[1],
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def delegate_single_mint(accounts, ntt, delegate_single):
    tx = ntt.mint(
        accounts[1],
        #"/delegate_minting.json",
        {'from': accounts[2]}
    )
    yield tx


@pytest.fixture
def delegate_batch(accounts, ntt):
    tx = ntt.delegateBatch(
        [accounts[1], accounts[2], accounts[3]],
        [accounts[2], accounts[3], accounts[4]],
        {'from': accounts[0]}
    )
    yield tx


@pytest.fixture
def delegate_batch_2(accounts, ntt):
    tx = ntt.delegateBatch(
        [accounts[1], accounts[1], ZERO_ADDRESS],
        [accounts[2], accounts[3], accounts[4]],
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
    assert ntt.supportsInterface(EIP_4671_ENUMERABLE_INTERFACE_ID) == 1
    assert ntt.supportsInterface(EIP_4671_DELEGATE_INTERFACE_ID) == 1
    assert ntt.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_mint(accounts, ntt, mint_a1_1):

    assert len(mint_a1_1.events) == 1
    assert mint_a1_1.events[0]["owner"] == accounts[1]
    assert mint_a1_1.events[0]["tokenId"] == 1
    assert mint_a1_1.events[0]["issuer"] == accounts[0]

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[0]
    assert ntt.isValid(1) == True
    assert ntt.ownerOf(1) == accounts[1]
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) == True
    assert ntt.tokenOfOwnerByIndex(accounts[1], 0) == 1
    #assert ntt.tokenURI(1) == "https://ntt.com/1.json"


def test_mint_non_owner_fail(accounts, ntt):

    with reverts("Address is not authorised to mint"):
        ntt.mint(
            accounts[2],
            #"/forbidden.json",
            {'from': accounts[1]}
        )


def test_mint_zero_address_fail(accounts, ntt):

    with reverts("Invalid address"):
        ntt.mint(
            ZERO_ADDRESS,
            #"/forbidden.json",
            {'from': accounts[0]}
        )


def test_invalidate(accounts, ntt, mint_a1_1, invalidate_a1_1):

    assert len(invalidate_a1_1.events) == 1
    assert invalidate_a1_1.events[0]["owner"] == accounts[1]
    assert invalidate_a1_1.events[0]["tokenId"] == 1

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[0]
    assert ntt.isValid(1) == False
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) == False


def test_mint_nonexistent_index_fail(accounts, ntt, mint_a1_1):

    with reverts("Token ID does not exist"):
        ntt.invalidate(
            2,
            {'from': accounts[0]}
        )


def test_invalidate_non_owner_fail(accounts, ntt, mint_a1_1):

    with reverts("Only owner is authorised to invalidate"):
        ntt.invalidate(
            1,
            {'from': accounts[2]}
        )


def test_multiple_mint_a1(accounts, ntt, mint_a1_1, mint_a1_2):

    assert len(mint_a1_2.events) == 1
    assert mint_a1_2.events[0]["owner"] == accounts[1]
    assert mint_a1_2.events[0]["tokenId"] == 2

    assert ntt.total() == 2
    assert ntt.issuerOf(2) == accounts[0]
    assert ntt.isValid(2) == True
    assert ntt.ownerOf(2) == accounts[1]
    assert ntt.balanceOf(accounts[1]) == 2
    assert ntt.hasValidToken(accounts[1]) == True
    #assert ntt.tokenURI(2) == "https://ntt.com/2.json"


def test_delegate(accounts, ntt, delegate_single):

    assert len(delegate_single.events) == 1
    assert delegate_single.events[0]["delegate"] == accounts[2]
    assert delegate_single.events[0]["recipient"] == accounts[1]

    assert ntt.canMint(accounts[2], accounts[1]) == True


def test_delegate_non_owner(accounts, ntt):

    with reverts("Only owner is authorised to delegate"):
        ntt.delegate(
            accounts[1],
            accounts[2],
            {'from': accounts[1]}
        )


def test_delegate_mint(accounts, ntt, delegate_single_mint):

    assert len(delegate_single_mint.events) == 1
    assert delegate_single_mint.events[0]["owner"] == accounts[1]
    assert delegate_single_mint.events[0]["tokenId"] == 1
    assert delegate_single_mint.events[0]["issuer"] == accounts[2]

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[2]
    assert ntt.isValid(1) == True
    assert ntt.ownerOf(1) == accounts[1]
    assert ntt.balanceOf(accounts[1]) == 1
    assert ntt.hasValidToken(accounts[1]) == True
    #assert ntt.tokenURI(1) == "https://ntt.com/delegate_minting.json"

    assert ntt.canMint(accounts[2], accounts[1]) == False


def test_delegate_batch(accounts, ntt, delegate_batch):

    assert len(delegate_batch.events["Delegate"]) == 3
    assert delegate_batch.events["Delegate"][0]["delegate"] == accounts[1]
    assert delegate_batch.events["Delegate"][0]["recipient"] == accounts[2]

    assert ntt.canMint(accounts[1], accounts[2]) == True

    assert delegate_batch.events["Delegate"][1]["delegate"] == accounts[2]
    assert delegate_batch.events["Delegate"][1]["recipient"] == accounts[3]

    assert ntt.canMint(accounts[2], accounts[3]) == True

    assert delegate_batch.events["Delegate"][2]["delegate"] == accounts[3]
    assert delegate_batch.events["Delegate"][2]["recipient"] == accounts[4]

    assert ntt.canMint(accounts[3], accounts[4]) == True


def test_delegate_batch_mint(accounts, ntt, delegate_batch):

    tx1 = ntt.mint(
        accounts[2],
        #'/1.json',
        {'from': accounts[1]}
    )

    assert len(tx1.events) == 1
    assert tx1.events[0]["owner"] == accounts[2]
    assert tx1.events[0]["tokenId"] == 1
    assert tx1.events[0]["issuer"] == accounts[1]

    assert ntt.total() == 1
    assert ntt.issuerOf(1) == accounts[1]
    assert ntt.isValid(1) == True
    assert ntt.ownerOf(1) == accounts[2]
    assert ntt.balanceOf(accounts[2]) == 1
    assert ntt.hasValidToken(accounts[2]) == True
    #assert ntt.tokenURI(1) == "https://ntt.com/1.json"

    assert ntt.canMint(accounts[1], accounts[2]) == False

    with reverts("Address is not authorised to mint"):
        ntt.mint(
            accounts[2],
            #'/invalid.json',
            {'from': accounts[1]}
        )

    tx2 = ntt.mint(
        accounts[3],
        #'/2.json',
        {'from': accounts[2]}
    )

    assert len(tx2.events) == 1
    assert tx2.events[0]["owner"] == accounts[3]
    assert tx2.events[0]["tokenId"] == 2
    assert tx2.events[0]["issuer"] == accounts[2]

    assert ntt.total() == 2
    assert ntt.issuerOf(2) == accounts[2]
    assert ntt.isValid(2) == True
    assert ntt.ownerOf(2) == accounts[3]
    assert ntt.balanceOf(accounts[3]) == 1
    assert ntt.hasValidToken(accounts[3]) == True
    #assert ntt.tokenURI(2) == "https://ntt.com/2.json"

    assert ntt.canMint(accounts[2], accounts[3]) == False

    with reverts("Address is not authorised to mint"):
        ntt.mint(
            accounts[3],
            #'/invalid.json',
            {'from': accounts[2]}
        )

    tx3 = ntt.mint(
        accounts[4],
        #'/3.json',
        {'from': accounts[3]}
    )

    assert len(tx3.events) == 1
    assert tx3.events[0]["owner"] == accounts[4]
    assert tx3.events[0]["tokenId"] == 3
    assert tx3.events[0]["issuer"] == accounts[3]

    assert ntt.total() == 3
    assert ntt.issuerOf(3) == accounts[3]
    assert ntt.isValid(3) == True
    assert ntt.ownerOf(3) == accounts[4]
    assert ntt.balanceOf(accounts[4]) == 1
    assert ntt.hasValidToken(accounts[4]) == True
    #assert ntt.tokenURI(3) == "https://ntt.com/3.json"

    assert ntt.canMint(accounts[3], accounts[4]) == False

    with reverts("Address is not authorised to mint"):
        ntt.mint(
            accounts[4],
            #'/invalid.json',
            {'from': accounts[3]}
        )


def test_delegate_batch_2(accounts, ntt, delegate_batch_2):

    assert len(delegate_batch_2.events["Delegate"]) == 2
    assert delegate_batch_2.events["Delegate"][0]["delegate"] == accounts[1]
    assert delegate_batch_2.events["Delegate"][0]["recipient"] == accounts[2]

    assert ntt.canMint(accounts[1], accounts[2]) == True

    assert delegate_batch_2.events["Delegate"][1]["delegate"] == accounts[1]
    assert delegate_batch_2.events["Delegate"][1]["recipient"] == accounts[3]

    assert ntt.canMint(accounts[1], accounts[3]) == True


def test_mint_batch(accounts, ntt, delegate_batch_2):

    tx = ntt.mintBatch(
        [accounts[2], accounts[3], ZERO_ADDRESS],
        #['/1.json', '/2.json', ''],
        {'from': accounts[1]}
    )

    assert len(tx.events["Mint"]) == 2
    assert tx.events["Mint"][0]["owner"] == accounts[2]
    assert tx.events["Mint"][0]["tokenId"] == 1
    assert tx.events["Mint"][0]["issuer"] == accounts[1]

    assert ntt.total() == 2

    assert ntt.issuerOf(1) == accounts[1]
    assert ntt.isValid(1) == True
    assert ntt.ownerOf(1) == accounts[2]
    assert ntt.balanceOf(accounts[2]) == 1
    assert ntt.hasValidToken(accounts[2]) == True
    #assert ntt.tokenURI(1) == "https://ntt.com/1.json"

    assert ntt.canMint(accounts[1], accounts[2]) == False

    assert tx.events["Mint"][1]["owner"] == accounts[3]
    assert tx.events["Mint"][1]["tokenId"] == 2
    assert tx.events["Mint"][1]["issuer"] == accounts[1]

    assert ntt.issuerOf(2) == accounts[1]
    assert ntt.isValid(2) == True
    assert ntt.ownerOf(2) == accounts[3]
    assert ntt.balanceOf(accounts[3]) == 1
    assert ntt.hasValidToken(accounts[3]) == True
    #assert ntt.tokenURI(2) == "https://ntt.com/2.json"

    assert ntt.canMint(accounts[1], accounts[3]) == False

    with reverts("Address is not authorised to mint"):
        ntt.mintBatch(
            [accounts[2], accounts[3], ZERO_ADDRESS],
            #['/1.json', '/2.json', ''],
            {'from': accounts[1]}
        )


def test_mint_batch_owner(accounts, ntt):

    tx = ntt.mintBatch(
        [accounts[2], accounts[3], accounts[4]],
        #['/1.json', '/2.json', '/3.json'],
        {'from': accounts[0]}
    )

    assert len(tx.events["Mint"]) == 3
    assert tx.events["Mint"][0]["owner"] == accounts[2]
    assert tx.events["Mint"][0]["tokenId"] == 1
    assert tx.events["Mint"][0]["issuer"] == accounts[0]

    assert ntt.total() == 3

    assert ntt.issuerOf(1) == accounts[0]
    assert ntt.isValid(1) == True
    assert ntt.ownerOf(1) == accounts[2]
    assert ntt.balanceOf(accounts[2]) == 1
    assert ntt.hasValidToken(accounts[2]) == True
    #assert ntt.tokenURI(1) == "https://ntt.com/1.json"

    assert ntt.canMint(accounts[1], accounts[2]) == False

    assert tx.events["Mint"][1]["owner"] == accounts[3]
    assert tx.events["Mint"][1]["tokenId"] == 2
    assert tx.events["Mint"][1]["issuer"] == accounts[0]

    assert ntt.issuerOf(2) == accounts[0]
    assert ntt.isValid(2) == True
    assert ntt.ownerOf(2) == accounts[3]
    assert ntt.balanceOf(accounts[3]) == 1
    assert ntt.hasValidToken(accounts[3]) == True
    #assert ntt.tokenURI(2) == "https://ntt.com/2.json"

    assert ntt.canMint(accounts[1], accounts[3]) == False

    assert tx.events["Mint"][2]["owner"] == accounts[4]
    assert tx.events["Mint"][2]["tokenId"] == 3
    assert tx.events["Mint"][2]["issuer"] == accounts[0]

    assert ntt.issuerOf(3) == accounts[0]
    assert ntt.isValid(3) == True
    assert ntt.ownerOf(3) == accounts[4]
    assert ntt.balanceOf(accounts[4]) == 1
    assert ntt.hasValidToken(accounts[4]) == True
    #assert ntt.tokenURI(3) == "https://ntt.com/3.json"

    assert ntt.canMint(accounts[0], accounts[4]) == False


def test_invalid_mint_batch(accounts, ntt):

    with reverts("Address is not authorised to mint"):
        ntt.mintBatch(
            [accounts[2], accounts[3], accounts[4]],
            #['/1.json', '/2.json', '/3.json'],
            {'from': accounts[1]}
        )

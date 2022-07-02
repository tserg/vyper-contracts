import pytest

from ape import (
    accounts,
    project,
    reverts,
)

from tests.constants import (
    ZERO_ADDRESS,
    ERC165_INTERFACE_ID,
    EIP_4671_INTERFACE_ID,
    EIP_4671_METADATA_INTERFACE_ID,
    EIP_4671_ENUMERABLE_INTERFACE_ID,
    EIP_4671_DELEGATE_INTERFACE_ID,
    INVALID_INTERFACE_ID,
)


@pytest.fixture(scope="class", autouse="True")
def ntt_delegate(accounts):
    c = project.NTTDelegate.deploy(
        "Non-Tradable Token",
        "NTT",
        "https://ntt.com",
        100,
        sender=accounts[0]
    )
    yield c


@pytest.fixture
def mint_a1_1(accounts, ntt_delegate):
    tx = ntt_delegate.mint(
        accounts[1],
        #"/1.json",
        sender=accounts[0]
    )
    yield tx


@pytest.fixture
def mint_a1_2(accounts, ntt_delegate):
    tx = ntt_delegate.mint(
        accounts[1],
        #"/2.json",
        sender=accounts[0]
    )
    yield tx


@pytest.fixture
def invalidate_a1_1(accounts, ntt_delegate):
    tx = ntt_delegate.invalidate(
        1,
        sender=accounts[0]
    )
    yield tx


@pytest.fixture
def delegate_single(accounts, ntt_delegate):
    tx = ntt_delegate.delegate(
        accounts[2],
        accounts[1],
        sender=accounts[0]
    )
    yield tx


@pytest.fixture
def delegate_single_mint(accounts, ntt_delegate, delegate_single):
    tx = ntt_delegate.mint(
        accounts[1],
        #"/delegate_minting.json",
        sender=accounts[2]
    )
    yield tx


@pytest.fixture
def delegate_batch(accounts, ntt_delegate):
    tx = ntt_delegate.delegateBatch(
        [accounts[1], accounts[2], accounts[3]],
        [accounts[2], accounts[3], accounts[4]],
        sender=accounts[0]
    )
    yield tx


@pytest.fixture
def delegate_batch_2(accounts, ntt_delegate):
    tx = ntt_delegate.delegateBatch(
        [accounts[1], accounts[1], ZERO_ADDRESS],
        [accounts[2], accounts[3], accounts[4]],
        sender=accounts[0]
    )
    yield tx


def test_start_state(ntt_delegate):

    assert ntt_delegate.name() == "Non-Tradable Token"
    assert ntt_delegate.symbol() == "NTT"
    assert ntt_delegate.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert ntt_delegate.supportsInterface(EIP_4671_INTERFACE_ID) == 1
    assert ntt_delegate.supportsInterface(EIP_4671_METADATA_INTERFACE_ID) == 1
    assert ntt_delegate.supportsInterface(EIP_4671_ENUMERABLE_INTERFACE_ID) == 1
    assert ntt_delegate.supportsInterface(EIP_4671_DELEGATE_INTERFACE_ID) == 1
    assert ntt_delegate.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_mint(accounts, ntt_delegate, mint_a1_1):

    events = list(mint_a1_1.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[0]

    assert ntt_delegate.total() == 1
    assert ntt_delegate.issuerOf(1) == accounts[0]
    assert ntt_delegate.isValid(1) == True
    assert ntt_delegate.ownerOf(1) == accounts[1]
    assert ntt_delegate.balanceOf(accounts[1]) == 1
    assert ntt_delegate.hasValidToken(accounts[1]) == True
    assert ntt_delegate.tokenOfOwnerByIndex(accounts[1], 0) == 1
    #assert ntt_delegate.tokenURI(1) == "https://ntt.com/1.json"


def test_mint_non_owner_fail(accounts, ntt_delegate):

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mint(
            accounts[2],
            #"/forbidden.json",
            sender=accounts[1]
        )


def test_mint_zero_address_fail(accounts, ntt_delegate):

    with reverts("Invalid address"):
        ntt_delegate.mint(
            ZERO_ADDRESS,
            #"/forbidden.json",
            sender=accounts[0]
        )


def test_invalidate(accounts, ntt_delegate, mint_a1_1, invalidate_a1_1):

    events = list(invalidate_a1_1.decode_logs(ntt_delegate.Invalidate))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1

    assert ntt_delegate.total() == 1
    assert ntt_delegate.issuerOf(1) == accounts[0]
    assert ntt_delegate.isValid(1) == False
    assert ntt_delegate.balanceOf(accounts[1]) == 1
    assert ntt_delegate.hasValidToken(accounts[1]) == False


def test_mint_nonexistent_index_fail(accounts, ntt_delegate, mint_a1_1):

    with reverts("Token ID does not exist"):
        ntt_delegate.invalidate(
            2,
            sender=accounts[0]
        )


def test_invalidate_non_owner_fail(accounts, ntt_delegate, mint_a1_1):

    with reverts("Only owner is authorised to invalidate"):
        ntt_delegate.invalidate(
            1,
            sender=accounts[2]
        )


def test_multiple_mint_a1(accounts, ntt_delegate, mint_a1_1, mint_a1_2):

    events = list(mint_a1_2.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 2

    assert ntt_delegate.total() == 2
    assert ntt_delegate.issuerOf(2) == accounts[0]
    assert ntt_delegate.isValid(2) == True
    assert ntt_delegate.ownerOf(2) == accounts[1]
    assert ntt_delegate.balanceOf(accounts[1]) == 2
    assert ntt_delegate.hasValidToken(accounts[1]) == True


def test_delegate(accounts, ntt_delegate, delegate_single):

    events = list(delegate_single.decode_logs(ntt_delegate.Delegate))
    assert len(events) == 1
    assert events[0].event_arguments["delegate"] == accounts[2]
    assert events[0].event_arguments["recipient"] == accounts[1]

    assert ntt_delegate.canMint(accounts[2], accounts[1]) == True


def test_delegate_non_owner(accounts, ntt_delegate):

    with reverts("Only owner is authorised to delegate"):
        ntt_delegate.delegate(
            accounts[1],
            accounts[2],
            sender=accounts[1]
        )


def test_delegate_mint(accounts, ntt_delegate, delegate_single_mint):

    events = list(delegate_single_mint.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[1]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[2]

    assert ntt_delegate.total() == 1
    assert ntt_delegate.issuerOf(1) == accounts[2]
    assert ntt_delegate.isValid(1) == True
    assert ntt_delegate.ownerOf(1) == accounts[1]
    assert ntt_delegate.balanceOf(accounts[1]) == 1
    assert ntt_delegate.hasValidToken(accounts[1]) == True

    assert ntt_delegate.canMint(accounts[2], accounts[1]) == False


def test_delegate_batch(accounts, ntt_delegate, delegate_batch):

    events = list(delegate_batch.decode_logs(ntt_delegate.Delegate))
    assert len(events) == 3
    assert events[0].event_arguments["delegate"] == accounts[1]
    assert events[0].event_arguments["recipient"] == accounts[2]

    assert ntt_delegate.canMint(accounts[1], accounts[2]) == True

    assert events[1].event_arguments["delegate"] == accounts[2]
    assert events[1].event_arguments["recipient"] == accounts[3]

    assert ntt_delegate.canMint(accounts[2], accounts[3]) == True

    assert events[2].event_arguments["delegate"] == accounts[3]
    assert events[2].event_arguments["recipient"] == accounts[4]

    assert ntt_delegate.canMint(accounts[3], accounts[4]) == True


def test_delegate_batch_mint(accounts, ntt_delegate, delegate_batch):

    tx1 = ntt_delegate.mint(
        accounts[2],
        #'/1.json',
        sender=accounts[1]
    )

    events = list(tx1.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[1]

    assert ntt_delegate.total() == 1
    assert ntt_delegate.issuerOf(1) == accounts[1]
    assert ntt_delegate.isValid(1) == True
    assert ntt_delegate.ownerOf(1) == accounts[2]
    assert ntt_delegate.balanceOf(accounts[2]) == 1
    assert ntt_delegate.hasValidToken(accounts[2]) == True
    #assert ntt_delegate.tokenURI(1) == "https://ntt_delegate.com/1.json"

    assert ntt_delegate.canMint(accounts[1], accounts[2]) == False

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mint(
            accounts[2],
            #'/invalid.json',
            sender=accounts[1]
        )

    tx2 = ntt_delegate.mint(
        accounts[3],
        #'/2.json',
        sender=accounts[2]
    )

    events = list(tx2.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[3]
    assert events[0].event_arguments["tokenId"] == 2
    assert events[0].event_arguments["issuer"] == accounts[2]

    assert ntt_delegate.total() == 2
    assert ntt_delegate.issuerOf(2) == accounts[2]
    assert ntt_delegate.isValid(2) == True
    assert ntt_delegate.ownerOf(2) == accounts[3]
    assert ntt_delegate.balanceOf(accounts[3]) == 1
    assert ntt_delegate.hasValidToken(accounts[3]) == True

    assert ntt_delegate.canMint(accounts[2], accounts[3]) == False

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mint(
            accounts[3],
            #'/invalid.json',
            sender=accounts[2]
        )

    tx3 = ntt_delegate.mint(
        accounts[4],
        #'/3.json',
        sender=accounts[3]
    )

    events = list(tx3.decode_logs(ntt_delegate.Mint))
    assert len(events) == 1
    assert events[0].event_arguments["owner"] == accounts[4]
    assert events[0].event_arguments["tokenId"] == 3
    assert events[0].event_arguments["issuer"] == accounts[3]

    assert ntt_delegate.total() == 3
    assert ntt_delegate.issuerOf(3) == accounts[3]
    assert ntt_delegate.isValid(3) == True
    assert ntt_delegate.ownerOf(3) == accounts[4]
    assert ntt_delegate.balanceOf(accounts[4]) == 1
    assert ntt_delegate.hasValidToken(accounts[4]) == True
    #assert ntt_delegate.tokenURI(3) == "https://ntt_delegate.com/3.json"

    assert ntt_delegate.canMint(accounts[3], accounts[4]) == False

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mint(
            accounts[4],
            #'/invalid.json',
            sender=accounts[3]
        )


def test_delegate_batch_2(accounts, ntt_delegate, delegate_batch_2):

    events = list(delegate_batch_2.decode_logs(ntt_delegate.Delegate))
    assert len(events) == 2
    assert events[0].event_arguments["delegate"] == accounts[1]
    assert events[0].event_arguments["recipient"] == accounts[2]

    assert ntt_delegate.canMint(accounts[1], accounts[2]) == True

    assert events[1].event_arguments["delegate"] == accounts[1]
    assert events[1].event_arguments["recipient"] == accounts[3]

    assert ntt_delegate.canMint(accounts[1], accounts[3]) == True


def test_mint_batch(accounts, ntt_delegate, delegate_batch_2):

    tx = ntt_delegate.mintBatch(
        [accounts[2], accounts[3], ZERO_ADDRESS],
        #['/1.json', '/2.json', ''],
        sender=accounts[1]
    )

    events = list(tx.decode_logs(ntt_delegate.Mint))
    assert len(events) == 2
    assert events[0].event_arguments["owner"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[1]

    assert ntt_delegate.total() == 2

    assert ntt_delegate.issuerOf(1) == accounts[1]
    assert ntt_delegate.isValid(1) == True
    assert ntt_delegate.ownerOf(1) == accounts[2]
    assert ntt_delegate.balanceOf(accounts[2]) == 1
    assert ntt_delegate.hasValidToken(accounts[2]) == True
    #assert ntt_delegate.tokenURI(1) == "https://ntt_delegate.com/1.json"

    assert ntt_delegate.canMint(accounts[1], accounts[2]) == False

    assert events[1].event_arguments["owner"] == accounts[3]
    assert events[1].event_arguments["tokenId"] == 2
    assert events[1].event_arguments["issuer"] == accounts[1]

    assert ntt_delegate.issuerOf(2) == accounts[1]
    assert ntt_delegate.isValid(2) == True
    assert ntt_delegate.ownerOf(2) == accounts[3]
    assert ntt_delegate.balanceOf(accounts[3]) == 1
    assert ntt_delegate.hasValidToken(accounts[3]) == True
    #assert ntt_delegate.tokenURI(2) == "https://ntt_delegate.com/2.json"

    assert ntt_delegate.canMint(accounts[1], accounts[3]) == False

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mintBatch(
            [accounts[2], accounts[3], ZERO_ADDRESS],
            #['/1.json', '/2.json', ''],
            sender=accounts[1]
        )


def test_mint_batch_owner(accounts, ntt_delegate):

    tx = ntt_delegate.mintBatch(
        [accounts[2], accounts[3], accounts[4]],
        #['/1.json', '/2.json', '/3.json'],
        sender=accounts[0]
    )

    events = list(tx.decode_logs(ntt_delegate.Mint))
    assert len(events) == 3
    assert events[0].event_arguments["owner"] == accounts[2]
    assert events[0].event_arguments["tokenId"] == 1
    assert events[0].event_arguments["issuer"] == accounts[0]

    assert ntt_delegate.total() == 3

    assert ntt_delegate.issuerOf(1) == accounts[0]
    assert ntt_delegate.isValid(1) == True
    assert ntt_delegate.ownerOf(1) == accounts[2]
    assert ntt_delegate.balanceOf(accounts[2]) == 1
    assert ntt_delegate.hasValidToken(accounts[2]) == True
    #assert ntt_delegate.tokenURI(1) == "https://ntt_delegate.com/1.json"

    assert ntt_delegate.canMint(accounts[1], accounts[2]) == False

    assert events[1].event_arguments["owner"] == accounts[3]
    assert events[1].event_arguments["tokenId"] == 2
    assert events[1].event_arguments["issuer"] == accounts[0]

    assert ntt_delegate.issuerOf(2) == accounts[0]
    assert ntt_delegate.isValid(2) == True
    assert ntt_delegate.ownerOf(2) == accounts[3]
    assert ntt_delegate.balanceOf(accounts[3]) == 1
    assert ntt_delegate.hasValidToken(accounts[3]) == True
    #assert ntt_delegate.tokenURI(2) == "https://ntt_delegate.com/2.json"

    assert ntt_delegate.canMint(accounts[1], accounts[3]) == False

    assert events[2].event_arguments["owner"] == accounts[4]
    assert events[2].event_arguments["tokenId"] == 3
    assert events[2].event_arguments["issuer"] == accounts[0]

    assert ntt_delegate.issuerOf(3) == accounts[0]
    assert ntt_delegate.isValid(3) == True
    assert ntt_delegate.ownerOf(3) == accounts[4]
    assert ntt_delegate.balanceOf(accounts[4]) == 1
    assert ntt_delegate.hasValidToken(accounts[4]) == True
    #assert ntt_delegate.tokenURI(3) == "https://ntt_delegate.com/3.json"

    assert ntt_delegate.canMint(accounts[0], accounts[4]) == False


def test_invalid_mint_batch(accounts, ntt_delegate):

    with reverts("Address is not authorised to mint"):
        ntt_delegate.mintBatch(
            [accounts[2], accounts[3], accounts[4]],
            #['/1.json', '/2.json', '/3.json'],
            sender=accounts[1]
        )

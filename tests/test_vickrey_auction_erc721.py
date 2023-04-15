import pytest
from ape import reverts
from eth_utils import to_wei


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


@pytest.fixture(scope="class", autouse=True)
def auction(accounts, project, erc721):
    c = project.vickrey_auction_ERC721.deploy(erc721.address, sender=accounts[0])
    yield c


@pytest.fixture
def initialise(accounts, chain, erc721, auction):
    erc721.approve(auction.address, 1, sender=accounts[0])

    start = auction.start_auction(
        to_wei(1, "ether"), chain.pending_timestamp + 100, 1, sender=accounts[0]
    )

    yield start


@pytest.fixture
def a1_first_bid(accounts, auction):

    tx = auction.bid(sender=accounts[1], value=to_wei(1.5, "ether"))
    return tx


@pytest.fixture
def a1_second_bid(accounts, auction, a1_first_bid):

    tx = auction.bid(sender=accounts[1], value=to_wei(0.5, "ether"))

    return tx


@pytest.fixture
def a2_first_bid(accounts, auction, a1_second_bid):

    tx = auction.bid(sender=accounts[2], value=to_wei(3, "ether"))

    return tx


@pytest.fixture
def close_auction(accounts, chain, auction, a2_first_bid):

    chain.mine(100)

    tx = auction.close(sender=accounts[0])

    return tx


def test_start_state(auction):

    assert auction.is_started() is False


def test_auction_started(auction, erc721, initialise):

    assert auction.is_started() is True
    assert auction.start_price() == to_wei(1, "ether")
    assert auction.token_id() == 1

    assert erc721.ownerOf(1) == auction


def test_bid(accounts, auction, initialise, a1_first_bid):

    events = list(a1_first_bid.decode_logs(auction.Bid))
    assert len(events) == 1
    assert events[0].event_arguments["value"] == to_wei(1.5, "ether")
    assert events[0].event_arguments["bidder"] == accounts[1]

    assert auction.get_highest_bid() == to_wei(1.5, "ether")
    assert auction.bids_to_bidder(to_wei(1.5, "ether")) == accounts[1]


def test_cumulative_bid_1(accounts, auction, initialise, a1_second_bid):

    events = list(a1_second_bid.decode_logs(auction.Bid))
    assert len(events) == 1
    assert auction.get_highest_bid() == to_wei(2, "ether")
    assert events[0].event_arguments["value"] == to_wei(2, "ether")
    assert events[0].event_arguments["bidder"] == accounts[1]

    assert auction.get_highest_bid() == to_wei(2, "ether")
    assert auction.bids_to_bidder(to_wei(2, "ether")) == accounts[1]


def test_competing_bid(accounts, auction, initialise, a2_first_bid):

    events = list(a2_first_bid.decode_logs(auction.Bid))
    assert len(events) == 1
    assert events[0].event_arguments["value"] == to_wei(3, "ether")
    assert events[0].event_arguments["bidder"] == accounts[2]

    assert auction.get_highest_bid() == to_wei(3, "ether")
    assert auction.bids_to_bidder(to_wei(3, "ether")) == accounts[2]
    assert auction.bidder_to_balance(accounts[1]) == to_wei(2, "ether")


def test_close(accounts, chain, erc721, auction, initialise, a2_first_bid):

    a0_balance = accounts[0].balance

    chain.mine(100)

    tx = auction.close(sender=accounts[0])

    assert erc721.ownerOf(1) == accounts[2]

    assert (
        accounts[0].balance
        == a0_balance + auction.get_second_highest_bid() - tx.total_fees_paid
    )
    assert auction.has_ended() is True


def test_refund_1(accounts, auction, initialise, close_auction):

    a1_balance = accounts[1].balance

    refund_tx_1 = auction.refund(sender=accounts[1])

    events = list(refund_tx_1.decode_logs(auction.Refund))
    assert len(events) == 1
    assert events[0].event_arguments["value"] == to_wei(2, "ether")
    assert events[0].event_arguments["bidder"] == accounts[1]

    assert (
        accounts[1].balance
        == a1_balance + to_wei(2, "ether") - refund_tx_1.total_fees_paid
    )
    assert auction.bidder_to_balance(accounts[1]) == 0


def test_refund_2(accounts, auction, initialise, close_auction):

    a2_balance = accounts[2].balance

    refund_tx = auction.refund(sender=accounts[2])

    events = list(refund_tx.decode_logs(auction.Refund))
    assert len(events) == 1
    assert events[0].event_arguments["value"] == to_wei(1, "ether")
    assert events[0].event_arguments["bidder"] == accounts[2]

    assert (
        accounts[2].balance
        == a2_balance + to_wei(1, "ether") - refund_tx.total_fees_paid
    )
    assert auction.bidder_to_balance(accounts[2]) == 0


def test_single_bid_wins(accounts, chain, auction, initialise, a1_first_bid):

    assert auction.get_second_highest_bid() == to_wei(1, "ether")

    a0_balance = accounts[0].balance

    chain.mine(100)

    close_tx = auction.close(sender=accounts[0])

    assert (
        accounts[0].balance
        == a0_balance + auction.get_second_highest_bid() - close_tx.total_fees_paid
    )
    assert auction.has_ended() is True

    refund_tx = auction.refund(sender=accounts[1])

    events = list(refund_tx.decode_logs(auction.Refund))
    assert len(events) == 1
    assert events[0].event_arguments["value"] == to_wei(0.5, "ether")
    assert events[0].event_arguments["bidder"] == accounts[1]


def test_illegal_close_auction_1(accounts, auction, initialise):

    assert auction.has_ended() is False

    with reverts("Auction has not ended"):
        auction.close(sender=accounts[0])

    assert auction.has_ended() is False


def test_illegal_close_auction_2(accounts, auction, initialise, a1_first_bid):

    assert auction.has_ended() is False

    with reverts("Auction has not ended"):
        auction.close(sender=accounts[0])

    assert auction.has_ended() is False


def test_no_bid_close(accounts, chain, erc721, auction, initialise):

    chain.mine(100)

    auction.close(sender=accounts[0])

    assert erc721.ownerOf(1) == accounts[0]
    assert auction.has_ended() is True

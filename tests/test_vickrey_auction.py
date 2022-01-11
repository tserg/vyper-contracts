import pytest

from brownie import (
    accounts,
    chain,
    reverts,
    Wei,
)

@pytest.fixture(scope="module", autouse=True)
def auction(accounts, VickreyAuction):
    c = VickreyAuction.deploy(
        Wei("1 ether"),
        chain.time() + 100000,
        {'from': accounts[0]}
    )
    yield c


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def a1_first_bid(accounts, auction):

    tx = auction.bid(
        {
            'from': accounts[1],
            'value': Wei("1.5 ether")
        }
    )
    return tx


@pytest.fixture
def a1_second_bid(accounts, auction, a1_first_bid):

    tx = auction.bid(
        {
            'from': accounts[1],
            'value': Wei("0.5 ether")
        }
    )

    return tx


@pytest.fixture
def a2_first_bid(accounts, auction, a1_second_bid):

    tx = auction.bid(
        {
            'from': accounts[2],
            'value': Wei("3 ether")
        }
    )

    return tx


@pytest.fixture
def close_auction(accounts, chain, auction, a2_first_bid):

    chain.sleep(100001)

    tx = auction.close({'from': accounts[0]})

    return tx


def test_start_state(auction):

    assert auction.get_highest_bid() == Wei("1 ether")
    assert auction.has_ended() == False


def test_bid(accounts, auction, a1_first_bid):

    assert len(a1_first_bid.events) == 1
    assert a1_first_bid.events[0]['value'] == Wei("1.5 ether")
    assert a1_first_bid.events[0]['bidder'] == accounts[1]

    assert auction.get_highest_bid() == Wei("1.5 ether")
    assert auction.bids_to_bidder(Wei("1.5 ether")) == accounts[1]


def test_cumulative_bid_1(accounts, auction, a1_second_bid):

    assert len(a1_second_bid.events) == 1
    assert auction.get_highest_bid() == Wei("2 ether")
    assert a1_second_bid.events[0]['value'] == Wei("2 ether")
    assert a1_second_bid.events[0]['bidder'] == accounts[1]

    assert auction.get_highest_bid() == Wei("2 ether")
    assert auction.bids_to_bidder(Wei("2 ether")) == accounts[1]


def test_competing_bid(accounts, auction, a2_first_bid):

    assert len(a2_first_bid.events) == 1
    assert a2_first_bid.events[0]['value'] == Wei("3 ether")
    assert a2_first_bid.events[0]['bidder'] == accounts[2]

    assert auction.get_highest_bid() == Wei("3 ether")
    assert auction.bids_to_bidder(Wei("3 ether")) == accounts[2]
    assert auction.bidder_to_balance(accounts[1]) == Wei("2 ether")


def test_close(accounts, chain, auction, a2_first_bid):

    a0_balance = accounts[0].balance()

    chain.sleep(100001)

    tx = auction.close({'from': accounts[0]})

    assert accounts[0].balance() == a0_balance + auction.get_second_highest_bid()
    assert auction.has_ended() == True


def test_refund_1(accounts, auction, close_auction):

    a1_balance = accounts[1].balance()

    refund_tx_1 = auction.refund({'from': accounts[1]})

    assert len(refund_tx_1.events) == 1
    assert refund_tx_1.events[0]['value'] == Wei("2 ether")
    assert refund_tx_1.events[0]['bidder'] == accounts[1]

    assert accounts[1].balance() == a1_balance + Wei("2 ether")
    assert auction.bidder_to_balance(accounts[1]) == 0


def test_refund_2(accounts, auction, close_auction):

    a1_balance = accounts[2].balance()

    refund_tx_1 = auction.refund({'from': accounts[2]})

    assert len(refund_tx_1.events) == 1
    assert refund_tx_1.events[0]['value'] == Wei("1 ether")
    assert refund_tx_1.events[0]['bidder'] == accounts[2]

    assert accounts[1].balance() == a1_balance + Wei("1 ether")
    assert auction.bidder_to_balance(accounts[2]) == 0

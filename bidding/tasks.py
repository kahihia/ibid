# -*- coding: utf-8 -*-

from threading import Timer
import logging

logger = logging.getLogger('django')

### from bidding.models import Auction
### from bidding.models import AuctionFixture


def _oldapi_start(auction):
    bid_number = 0
    if auction.status == 'waiting':
        auction.start()
    elif auction.status == 'pause':
        auction.resume()
        bid_number = auction.getBidNumber()
    finish_auction(auction, bid_number, auction.auction.bidding_time)


def _oldapi_finish(auction, bid_number):
    if auction.status == 'processing' and bid_number == auction.used_bids()/auction.minimum_precap:
        auction.finish()
        auction.create_from_fixtures()


def start_auction(auction, delay):
    kwargs = {'auction': auction}
    t = Timer(delay, _oldapi_start, kwargs=kwargs)
    t.start()


def finish_auction(auction, bid_number, delay):
    kwargs = {'auction': auction, 'bid_number': bid_number}
    t = Timer(delay, _oldapi_finish, kwargs=kwargs)
    t.start()

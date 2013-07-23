# -*- coding: utf-8 -*-

from threading import Timer
import logging

logger = logging.getLogger('django')

#from bidding.models import Auction


def _oldapi_start(auction):
    if auction.status == 'waiting':
        auction.start()
        bid_number = 0
    elif auction.status == 'pause':
        auction.resume()
        bid_number = auction.getBidNumber()
    finish_auction(auction, bid_number, auction.auction.bidding_time)


def _oldapi_finish(auction, bif_number):
    if auction.status == 'processing' and bid_number == auction.used_bids()/auction.minimum_precap:
        # finish
        auction.finish()

        # run auction fixtures #
        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='token')) == 0:
            aifx = AuctionFixture.objects.filter(bid_type='token')
            if len(aifx):
                rt = aifx[0].make_auctions()

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='bid')) == 0:
            aifx = AuctionFixture.objects.filter(bid_type='bid')
            if len(aifx):
                rt = aifx[0].make_auctions()


def add_timer(fn, kwargs, delay):
    t = Timer(delay, fn, kwargs=kwargs)
    t.start()


def start_auction(auctiond, delay):
    _add_timer(_oldapi_start, {'auction': auction}, delay)


def finish_auction(auction, bid_number, delay):
    _add_timer(_oldapi_finish, {'auction': auction, 'bid_number': bid_number}, delay)

# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from decimal import Decimal
import logging
import time
import urllib, urllib2

logger = logging.getLogger('django')

from django.conf import settings

from bidding import client
from bidding.signals import auction_finished_signal, send_in_thread, precap_finished_signal
from bidding.signals import task_auction_start, task_auction_pause


# oldclient_* functions are what originally were at bid_client.py file
def oldclient_delayStart(auctionId, bidNumber, time):
    print "client delayStart", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'startCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'startCountDown/?%s' % urllib.urlencode(kwargs))


def oldclient_bid(auctionId, bidNumber, time):
    print "client bid", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'stopCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))


def oldclient_delayResume(auctionId, bidNumber, time):
    print "client delayResume", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'startCountDown/?%s' % urllib.urlencode(kwargs))


def oldclient_delayStop(auctionId, bidNumber, time):
    print "client delayStop", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'stopCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))


def oldclient_resume(auctionId, bidNumber, time):
    print "client resume", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))


def oldclient_finish(auctionId, bidNumber, time):
    print "client finish", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.BID_SERVICE + 'finish/?%s' % urllib.urlencode(kwargs))




class AuctionDelegate(object):
    def __init__(self, auction):
        self.auction = auction


class StateAuctionDelegate(AuctionDelegate):
    def get_last_bidder(self):
        """ 
        Returns the last member that placed a bid on this auction or None. 
        """

        #TODO see if it's necessary
        bid = self.auction.get_latest_bid()
        return bid.bidder if bid else None

    def get_latest_bid(self):
        """
        Returns the most recent bid of the auction.
        """

        bid_query = self.auction.bid_set.order_by('-unixtime')
        return bid_query[0] if bid_query else None

    def get_time_left(self):
        #shouldnt be necessary
        return None


class PrecapAuctionDelegate(StateAuctionDelegate):
    def can_precap(self, member, amount):
        """ 
        Returns True if the member can place the specified amount of precap
        bids in this auction.
        """
        return member.get_bids(self.auction.bid_type) + member.get_placed_amount(self.auction) >= amount

    def completion(self):
        """ Returns a completion percentaje (0-100 integer) of the precap. """

        return int((self.auction.placed_bids() * 100) / self.auction.precap_bids)

    def place_precap_bid(self, member, amount):
        """ 
        The member commits an amount precap bid to the auction and saves its 
        state. 
        Checks if the auction precap should be finished.
        Returns True if the member just joined the auction.
        """

        joining = not self.auction.has_joined(member)

        if joining:
            self.auction.bidders.add(member)

        member.precap_bids(self.auction, amount)

        #TODO two users can enter here because status is not yet changed
        if not self.auction._precap_bids_needed():
            self.auction.finish_precap()

        return joining

    def leave_auction(self, member):
        """ Returns all the bids commited to the auction by the member. """

        self.auction.bidders.remove(member)
        member.leave_auction(self.auction)

    def _precap_bids_needed(self):
        """ 
        Returns the amount of bids needed before the precap is finished. 
        """

        needed = self.auction.precap_bids - self.auction.placed_bids()

        return needed if needed > 0 else 0


    def _check_preload_auctions(self):
        """ 
        Checks the amount of upcoming auctions, and runs a fixture in case 
        there are not enough. 
        """
        from models import Auction, AuctionFixture

        upcoming = Auction.objects.filter(bid_type=self.auction.bid_type,
                                          is_active=True, status__in='precap').count()

        for fixture in AuctionFixture.objects.filter(
                bid_type=self.auction.bid_type,
                automatic=True):
            if fixture.threshold > upcoming:
                fixture.make_auctions()

    def finish_precap(self):
        """
        Changes the status to Waiting, sets the auction start date and saves
        it.
        """
        self.auction.status = 'waiting'
        self.auction.start_date = datetime.now() + timedelta(seconds=5)
        self.auction.save()

        from chat import auctioneer

        auctioneer.precap_finished_message(self.auction)

        client.auctionAwait(self.auction)

        oldclient_delayStart(self.auction.id, 0, 5.0)

        send_in_thread(precap_finished_signal, sender=self, auction=self.auction)


class WaitingAuctionDelegate(StateAuctionDelegate):
    def can_precap(self, member, amount):
        """ 
        Returns True if the member can place the specified amount of precap
        bids in this auction.
        """

        #return member.bids_left >= amount and not self.auction.has_joined(member)
        return (member.get_bids(self.auction.bid_type) >= amount
                and not self.auction.has_joined(member))

    def place_precap_bid(self, member, amount):
        """ 
        The member joins the auction. No validations are made (can_precap 
        is assumed to be True).
        """

        self.auction.bidders.add(member)
        member.precap_bids(self.auction, amount)

        return True

    def start(self):
        """ Starts the auction and saves the model. """

        self.auction.status = 'processing'
        client.auctionActive(self.auction)
        self.auction.saved_time = self.auction.bidding_time
        self.auction.save()

    def get_time_left(self):
        start_time = Decimal("%f" % time.mktime(
            self.auction.start_date.timetuple()))
        return float(start_time) - time.time()


class RunningAuctionDelegate(StateAuctionDelegate):
    def get_last_bidder(self):
        """ 
        Returns the username of the last member that placed a bid on this 
        auction. 
        """

        qs = self.auction.bid_set.order_by('-unixtime')

        if not qs or not qs[0].used_amount > 0:
            return None

        return qs[0].bidder

    def finish(self):
        """ Marks the auction as finished, sets the winner and win time. """
        logger.debug("Entering finish")

        bidder = self.auction.get_last_bidder()
        self.auction.winner = bidder.user if bidder else None
        self.auction.won_price = self.auction.price()
        self.auction.status = 'waiting_payment'
        self.auction.won_date = datetime.now()
        self.auction.save()
        logger.debug("Ended auction saved")

        from chat import auctioneer

        auctioneer.auction_finished_message(self.auction)

        client.auctionFinish(self.auction)

        send_in_thread(auction_finished_signal, sender=self, auction=self.auction)
        logger.debug("Sent signal")


    def can_bid(self, member):
        """
        Returns True if the member has commited bids left to use on the 
        auction, and its not the last bidder. 
        """

        if self.auction.get_last_bidder() == member:
            return False

        return member.auction_bids_left(self.auction)

    def _check_thresholds(self):
        """ 
        Checks if a threshold has been reached, and modifies the bidding time
        accordingly. If a threshold is reached True is returned.        
        """
        current_bids = self.auction.used_bids()
        limt_bids = int(self.auction.placed_bids() * 0.25)

        while limt_bids % self.auction.minimum_precap <> 0:
            limt_bids -= 1

        from chat.auctioneer import threshold_message

        if self.auction.threshold1 and current_bids == limt_bids:
            self.auction.bidding_time = self.auction.threshold1
            threshold_message(auction=self.auction, number=1)
            return True
        if self.auction.threshold2 and current_bids == 2 * limt_bids:
            self.auction.bidding_time = self.auction.threshold2
            threshold_message(auction=self.auction, number=2)
            return True
        if self.auction.threshold3 and current_bids == 3 * limt_bids:
            self.auction.bidding_time = self.auction.threshold3
            threshold_message(auction=self.auction, number=3)
            return True
        return False

    def bid(self, member):
        """ 
        Uses one of the member's commited bids in the auction.
        """
        bid = self.auction.bid_set.get(bidder=member)
        bid.used_amount += self.auction.minimum_precap
        bid_time = time.time()
        bid.unixtime = Decimal("%f" % bid_time)
        bid.save()
        if self._check_thresholds():
            self.auction.pause()
            oldclient_delayResume(self.auction.id, self.auction.getBidNumber(), self.auction.bidding_time)
        else:
            oldclient_bid(self.auction.id, self.auction.getBidNumber(), self.auction.bidding_time)

    def get_time_left(self):
        bid = self.auction.get_latest_bid()
        if bid:
            if bid.used_amount == 0:
                #if its the first bid, the base is the start date
                start_time = Decimal("%f" % time.mktime(
                    self.auction.start_date.timetuple()))
            else:
                start_time = bid.unixtime
            time_left = (float(self.auction.bidding_time)
                         - time.time() + float(start_time))
            return round(time_left) if time_left > 0 else 0
        return None

    def pause(self):
        """ pauses the auction. """
        self.auction.status = 'pause'
        self.auction.save()
        client.auctionPause(self.auction)
        oldclient_delayResume(self.auction.id, self.auction.getBidNumber(), 10)
        send_in_thread(task_auction_pause, sender=self, auction=self.auction)


class PausedAuctinoDelegate(StateAuctionDelegate):
    def resume(self):
        """ Resumes the auction. """

        self.auction.status = 'processing'
        self.auction.saved_time = self.auction.bidding_time
        self.auction.save()

        #fixme ugly
        bid = self.auction.get_latest_bid()
        now = time.time()
        bid.unixtime = Decimal("%f" % now)
        bid.save()

        client.auctionResume(self.auction)


state_delegates = {
    u'precap': PrecapAuctionDelegate,
    u'waiting': WaitingAuctionDelegate,
    u'processing': RunningAuctionDelegate,
    u'pause': PausedAuctinoDelegate,
    u'waiting_payment': StateAuctionDelegate,
    u'paid': StateAuctionDelegate,
}

all_delegates = [
    PrecapAuctionDelegate,
    WaitingAuctionDelegate,
    RunningAuctionDelegate,
    PausedAuctinoDelegate,
]


class GlobalAuctionDelegate(object):
    def __init__(self, auction):
        self.auction = auction
        self.id = auction.id

    def __getattr__(self, name):
        for sd in all_delegates:
            if hasattr(sd, name):
                return getattr(sd(self.auction), name)
        if hasattr(self.auction, name):
            return getattr(self.auction, name)
        raise AttributeError





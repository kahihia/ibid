__author__ = 'dnuske'


import sys
import os
import urllib
import time

sys.path.append('/var/www/ibiddjango/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ibiddjango.settings'

from bidding.models import Auction

statuses = {
    'precap': 0,
    'waiting': 1,
    'processing': 2,
    'pause': 2,
    'waiting_payment': 4,
    'paid': 5
};

class TestAuctioneer(object):
    def __init__(self, userId, auctionId):
        self.userId = userId
        self.auctionId = auctionId
        self.credits = 0
        self.tokens = 0
        self._neverBidded = True
        #TODO take values from database

    #precap
    def startBidding(self):
        print "startBidding"
        urllib.urlopen("http://localhost:8000/apitest/startBidding/?id=%s&memberId=%s" % (self.auctionId, self.userId))
        self._neverBidded = False

    def addBids(self):
        print "addBids"
        urllib.urlopen("http://localhost:8000/apitest/addBids/?id=%s&memberId=%s" % (self.auctionId, self.userId))

    #processing
    def claim(self):
        print "claim"
        urllib.urlopen("http://localhost:8000/apitest/claim/?id=%s&memberId=%s" % (self.auctionId, self.userId))

    def do(self, auctionStatus):
        if self._neverBidded:
            self.startBidding()
        elif auctionStatus == 'precap':
            self.addBids()
        elif auctionStatus == 'processing':
            self.claim()


class TestAuction(object):
    def __init__(self, auctionId):
        self.auction = Auction.objects.get(id=auctionId)


def test(auctionId):

    a = TestAuction(auctionId).auction
    u = {
        'a': TestAuctioneer(4, a.id),
        'b': TestAuctioneer(5, a.id),
        'c': TestAuctioneer(6, a.id)
        }

    auctionFinished = False
    while not auctionFinished:
        print "new loop"
        print a.status
        for i,j in u.items():
            j.do(a.status)

        time.sleep(2)
        a = TestAuction(auctionId).auction
        auctionFinished = (a.status == 'waiting_payment')

test(18)

__author__ = 'dnuske'

import sys
import os
import urllib
import time
import threading
from random import randint
from time import sleep

from django.db import transaction

# sys.path.append('/var/www/ibiddjango/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ibiddjango.settings'

GAME_URL = 'http://localhost:8000/'
GAME_URL = 'http://apps.facebook.ibidgames.com/'

from bidding.models import Auction

statuses = {
    'precap': 0,
    'waiting': 1,
    'processing': 2,
    'pause': 2,
    'waiting_payment': 4,
    'paid': 5
};

class Client(object):
    def __init__(self, userId, auctionId):
        self.userId = userId
        self.auctionId = auctionId
        self.credits = 0
        self.tokens = 0
        self._neverBidded = True
        #TODO take values from database

        auctionFinished = False
        while not auctionFinished:
            sleepTime = float(str(randint(0,20000)).zfill(3))/100
            sleep(sleepTime)
            print "new loop", TestAuction(auctionId).auction.status, sleepTime

            self.do(TestAuction(auctionId).auction.status)

            auctionFinished = (TestAuction(auctionId).auction.status == 'waiting_payment')

            transaction.enter_transaction_management()
            transaction.commit() # Whenever you want to see new data

        print "DONE: client " + str(self.userId)

    def getAuctionStatus(self):
        print self.userId, "getAuctionStatus"
        tmp = urllib.urlopen(GAME_URL+"apitest/getAuctionStatus/?id=%s" % (self.auctionId,))
        return tmp.read()


    #precap
    def startBidding(self):
        print self.userId, "startBidding"
        self._send(GAME_URL+"apitest/startBidding/?id=%s&memberId=%s" % (self.auctionId, self.userId))
        self._neverBidded = False

    def addBids(self):
        print self.userId, "addBids"
        self._send(GAME_URL+"apitest/addBids/?id=%s&memberId=%s" % (self.auctionId, self.userId))

    #processing
    def claim(self):
        print self.userId, "claim"
        self._send(GAME_URL+"apitest/claim/?id=%s&memberId=%s" % (self.auctionId, self.userId))

    def do(self, auctionStatus):
        if self._neverBidded:
            self.startBidding()
        elif auctionStatus == 'precap':
            self.addBids()
        elif auctionStatus == 'processing':
            self.claim()

    def _send(self, url):
        urllib.urlopen(url)
        # th = threading.Thread(target=urllib.urlopen, args=[url])
        # th.start()

class TestAuction(object):
    def __init__(self, auctionId):
        self.auction = Auction.objects.get(id=auctionId)

def test(auctionId, clientIds):

    print "starting threads"
    ths = []
    for i in clientIds:
        print " . "
        th = threading.Thread(target=Client, args=[i, auctionId])
        #th.daemon = True
        th.start()
        ths.append(th)

    while threading.active_count() > 0:
        time.sleep(0.1)



auctionId = 52
clientsIds = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
              56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]

test(auctionId, clientsIds)


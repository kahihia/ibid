#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setproctitle, logging
from threading import Timer, _Timer
from multiprocessing import Process, Pipe

from django.utils import simplejson as json

from bid_client import bidServerClient
from bidding.models import Auction, AuctionFixture
from bidding import client
from bidding.delegate import GlobalAuctionDelegate
import settings

# ----------------- LOG config ----------------- 

logger = logging.getLogger('bid_server')
hdlr = logging.FileHandler('../logs/bid_server.log')
formatter = logging.Formatter("%(asctime)-15s  %(message)s") #TODO: log user facebook_id on every action
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

d = {'auctionId': '_'}

logger.info(' --- Starting bid_server ---')

# --- change process name --- 
setproctitle.setproctitle('bidsrvr')

IM_ALIVE = 'IM_ALIVE'
KILL_SIGNAL = 'KILL_SIGNAL'

liveAuctionsStack = {}



class LiveAuction:
    def __init__(self, child_conn, auctionId):
        logger.info(" - - %s liveAuction init", auctionId)
        self.id = auctionId
        self.t = None
        self.auction = GlobalAuctionDelegate(Auction.objects.get(id=auctionId))

        d['auctionId'] = auctionId

        setproctitle.setproctitle('bidsrvr %s' % str(self.id))

        try:
            while True: #must be run
                #try:
                logger.info(" - - %s waiting for message", str(self.id))
                rawmsg = child_conn.recv()

                logger.info(" - - %s raw message: %s", str(self.id), str(rawmsg))

                # --- calling self function --- 
                msg = json.loads(rawmsg)
                ret = getattr(self, msg['method'])(**msg['params'])

                # --- giving the result to parent process ---
                logger.info(" - - Actually the return: %s" % str(ret))
                child_conn.send({True:KILL_SIGNAL, False:json.dumps(['OK'])}[ret == KILL_SIGNAL])

                # --- kill LiveAuction process when finished --- 
                if ret and ret == KILL_SIGNAL:
                    logger.info(" - - %s END PROCESS", str(self.id))
                    #break
        except:
            logger.exception(" - - ERROR PROCESS")
            setproctitle.setproctitle('bidsrvr %s <ERROR>' % str(self.id))
            child_conn.send(json.dumps(['ERROR']))

    def wait(self, **kwargs):
        logger.info(' - - %s liveAuction wait', str(self.id))
        self.auction = GlobalAuctionDelegate(Auction.objects.get(id=self.auction.id))
        self.start()

    def start(self, timeLeft=0):
        logger.info(' - - %s liveAuction start, timeleft:%s', str(self.id), str(timeLeft))
        self.auction = GlobalAuctionDelegate(Auction.objects.get(id=self.auction.id))
        self.auction.start()
        # --- delay the LiveAuction stop call to be called if no one bid --- 
        self.delayMethod(self.callStop, time=timeLeft, auctionId=self.id)

    def bid(self, timeLeft=0):
        logger.info(' - - %s liveAuction bid, timeleft:%s', self.id, str(timeLeft))
        # --- delay the LiveAuction stop call to be called if no one else bid --- 
        self.delayMethod(self.callStop, time=timeLeft, auctionId=self.id)

    def pause(self, timeLeft=0):
        logger.info(' - - %s liveAuction pause, timeleft:%s', str(self.id), str(timeLeft))
        # --- delay the LiveAuction resume --- 
        self.delayMethod(self.callResume, time=timeLeft, auctionId=self.id)

    def finish(self):

        self.auction = GlobalAuctionDelegate(Auction.objects.get(id=self.auction.id))
        logger.info(' - - %s finish', self.id)
        self.auction.finish()

        #run auction fixtures
        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='token')) == 0:
            #run first token fixture
            aifx = AuctionFixture.objects.filter(bid_type='token')
            if len(aifx):
                rt = aifx[0].make_auctions()
                print "rt = aifx[0].make_auctions()", rt
                for auct in rt:
                    client.auction_created(auct)

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='bid')) == 0:
            #run first bids fixture
            aifx = AuctionFixture.objects.filter(bid_type='bid')
            if len(aifx):
                rt = aifx[0].make_auctions()
                print "rt = aifx[0].make_auctions()", rt
                for auct in rt:
                    client.auction_created(auct)

        return KILL_SIGNAL

    def resume(self, timeLeft=0):
        self.auction = GlobalAuctionDelegate(Auction.objects.get(id=self.auction.id))
        logger.info(' - - %s resume', self.id)
        logger.info(' - - %s auction current status %s', self.id, str(self.auction.auction.status))
        self.auction.resume()

        self.delayMethod(self.callStop, time=self.auction.auction.bidding_time, auctionId=self.id)

    def delayMethod(self, method, **kwargs): #auctionId, bidId, method, time):
        logger.info(" - - %s delayMethod " + str(method) + str(kwargs), self.id)
        time = kwargs['time']
        del kwargs['time']
        if type(self.t) is _Timer:
            self.t.cancel()

        self.t = Timer(time, method, kwargs=kwargs)
        self.t.start()

    def callStop(self, auctionId=None):
        logger.info(" - - %s callStop", str(self.id))
        bidServerClient.finish(auctionId)

    def callResume(self, auctionId=None):
        logger.info(" - - %s callResume", str(self.id))
        bidServerClient.resume(auctionId)


def process(auctionId, method, params):
    """
    LiveAuction stack manager
    """

    if method == IM_ALIVE:
        logger.info(' - IM_ALIVE')
        # --- self telling I'M Alive every 30 minutes --- 
        t = Timer(1800, bidServerClient.imAlive)
        t.start()

    else:
        if auctionId not in liveAuctionsStack.keys():
            if method in ('start', 'wait'):
                logger.info(" - BEGIN LiveAuction process")
                parent_conn, child_conn = Pipe()
                p = Process(target=LiveAuction, args=(child_conn, auctionId))
                p.start()

                liveAuctionsStack[auctionId] = {'pipe': {'parent': parent_conn}, 'process': p}
            else:
                #ignore messages that come when auction already ended!
                return True

        liveAuctionsStack[auctionId]['pipe']['parent'].send(json.dumps({'method': method, 'params': params}))
        res = liveAuctionsStack[auctionId]['pipe']['parent'].recv()

        # --- if closing from inside, just end the process --- 
        if res == KILL_SIGNAL:
            logger.info(" - TERMINATE LiveAuction process")
            liveAuctionsStack[auctionId]['process'].terminate()

        return res


def receive(message):
    try:
        logger.info("process receive: %s" % message)
        msg = message
        response = process(msg['auctionId'], msg['method'], msg['params'])
        logger.info("process return: %s" % response)
    except Exception, e:
        logger.exception(e)
    finally:
        return True


# --- starting AMQP connection ---
from Pubnub import Pubnub

pubnub = Pubnub(settings.PUBNUB_PUB, settings.PUBNUB_SUB, None, False)
channel = 'rpc_queue'


def subscribe():
    print("Listening for messages on '%s' channel..." % channel)
    pubnub.subscribe({
        'channel': channel,
        'callback': receive
    })

print("waiting for subscribes and presence")
subscribe()


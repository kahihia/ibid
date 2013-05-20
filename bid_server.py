#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import os
#os.environ['DJANGO_SETTINGS_MODULE']='ibiddjango.settings'

import setproctitle, sys, logging, time
from threading import Timer, _Timer
from datetime import datetime, timedelta
from multiprocessing import Process, Pipe

from django.utils import simplejson as json

from bid_client import bidServerClient
from bidding.models import Auction, AuctionFixture
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
        logger.info("%s liveAuction init", auctionId)
        self.id = auctionId
        self.t = None
        self.auction = Auction.objects.get(id=self.id)

        d['auctionId'] = auctionId

        setproctitle.setproctitle('bidsrvr %s' % str(self.id))

        try:
            while True: #must be run
                #try:
                logger.info("%s waiting for message", str(self.id))
                rawmsg = child_conn.recv()

                logger.info("%s raw message: %s", str(self.id), str(rawmsg))

                # --- calling self function --- 
                msg = json.loads(rawmsg)
                ret = getattr(self, msg['method'])(**msg['params'])

                # --- giving the result to parent process --- 
                child_conn.send(json.dumps(['OK']))

                # --- kill LiveAuction process when finished --- 
                if ret and ret == KILL_SIGNAL:
                    logger.info("%s END PROCESS", str(self.id))
                    break
        except:
            logger.exception("ERROR PROCESS")
            setproctitle.setproctitle('bidsrvr %s <ERROR>' % str(self.id))
            child_conn.send(json.dumps(['ERROR']))

    def wait(self, **kwargs):
        logger.info('%s liveAuction wait', str(self.id))
        self.auction = Auction.objects.get(id=self.auction.id)
        self.start()

    def start(self, timeLeft=0):
        logger.info('%s liveAuction start, timeleft:%s', str(self.id), str(timeLeft))
        self.auction = Auction.objects.get(id=self.auction.id)
        self.auction.start()
        # --- delay the LiveAuction stop call to be called if no one bid --- 
        self.delayMethod(self.callStop, time=timeLeft, auctionId=self.id)

    def bid(self, timeLeft=0):
        logger.info('%s liveAuction bid, timeleft:%s', self.id, str(timeLeft))
        # --- delay the LiveAuction stop call to be called if no one else bid --- 
        self.delayMethod(self.callStop, time=timeLeft, auctionId=self.id)

    def pause(self, timeLeft=0):
        logger.info('%s liveAuction pause, timeleft:%s', str(self.id), str(timeLeft))
        # --- delay the LiveAuction resume --- 
        self.delayMethod(self.callResume, time=timeLeft, auctionId=self.id)

    def finish(self):
        self.auction = Auction.objects.get(id=self.auction.id)
        logger.info('%s finish', self.id)
        self.auction.finish()

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='token')) == 0:
            #run first token fixture
            aifx = AuctionFixture.objects.filter(bid_type='token')
            if len(aifx):
                aifx[0].make_auctions()

        #check if no bid precap auctioos
        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='bid')) == 0:
            #run first bids fixture
            aifx = AuctionFixture.objects.filter(bid_type='bid')
            if len(aifx):
                aifx[0].make_auctions()

        return KILL_SIGNAL

    def resume(self, **kwargs):
        self.auction = Auction.objects.get(id=self.auction.id)
        logger.info('%s resume', self.id)
        logger.info('%s auction current status %s', self.id, str(self.auction.status))
        self.auction.resume()

    def delayMethod(self, method, **kwargs): #auctionId, bidId, method, time):
        logger.info("%s delayMethod " + str(method) + str(kwargs), self.id)
        time = kwargs['time']
        del kwargs['time']
        if type(self.t) is _Timer:
            self.t.cancel()

        self.t = Timer(time, method, kwargs=kwargs)
        self.t.start()

    def callStop(self, auctionId=None):
        logger.info("%s callStop", str(self.id))
        bidServerClient.finish(auctionId)

    def callResume(self, auctionId=None):
        logger.info("%s callResume", str(self.id))
        bidServerClient.resume(auctionId)


def process(auctionId, method, params):
    """
    LiveAuction stack manager
    """

    if method == IM_ALIVE:
        logger.info('IM_ALIVE')
        # --- self telling I'M Alive every 30 minutes --- 
        t = Timer(1800, bidServerClient.imAlive)
        t.start()

    else:
        if auctionId not in liveAuctionsStack.keys():
            logger.info("BEGIN LiveAuction process")
            parent_conn, child_conn = Pipe()
            p = Process(target=LiveAuction, args=(child_conn, auctionId))
            p.start()

            liveAuctionsStack[auctionId] = {'pipe': {'parent': parent_conn}, 'process': p}

        liveAuctionsStack[auctionId]['pipe']['parent'].send(json.dumps({'method': method, 'params': params}))
        res = liveAuctionsStack[auctionId]['pipe']['parent'].recv()

        # --- if closing from inside, just end the process --- 
        if res == KILL_SIGNAL:
            logger.info("TERMINATE LiveAuction process")
            liveAuctionsStack[auctionId]['process'].terminate()

        return res


# def on_request(ch, method, props, body):
#     logger.info("on_request : %s" % body)
#     msg = json.loads(body)
#     if len(sys.argv) > 1 and sys.argv[1] == 'purge':
#         logger.info("lost msg: %s" % body)
#         response = 'asd'
#     else:
#         response = process(msg['auctionId'], msg['method'], msg['params'])
#     logger.info("process return: %s" % response)
#
#     ch.basic_publish(exchange='',
#                      routing_key=props.reply_to,
#                      properties=pika.BasicProperties(correlation_id=props.correlation_id),
#                      body=json.dumps(response))
#     ch.basic_ack(delivery_tag=method.delivery_tag)


def receive(message):
    try:
        logger.info("receive : %s" % message)
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

#msgModel = {'auctionId':0, 'method':'', 'params':{}}




# # --- starting AMQP connection ---
# AMQPconn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
# AMQPchannel = AMQPconn.channel()
# AMQPchannel.queue_declare(queue='rpc_queue')
#
# AMQPchannel.basic_qos(prefetch_count=1)
# AMQPchannel.basic_consume(on_request, queue='rpc_queue')
#
# # --- shedule ahead 20 seconds the first IM_ALIVE message ---
# e = Timer(20, bidServerClient.imAlive) #'auctionId':0, 'method':'', 'params':{}}}])
# e.start()
#
# while True:
#     logger.info( " [x] Awaiting RPC requests")
#     AMQPchannel.start_consuming()
#
# #msgModel = {'auctionId':0, 'method':'', 'params':{}}

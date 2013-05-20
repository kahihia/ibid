# -*- coding: utf-8 -*-
'''
client interface to bid_server
'''


from django.utils import simplejson as json


import uuid
import urllib
import settings


class BidServerClient(object):
    def __init__(self):
        pass
        #self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        #self.channel = self.connection.channel()

        #result = self.channel.queue_declare(exclusive=True)
        #self.callback_queue = result.method.queue

        #self.channel.basic_consume(self.on_response, no_ack=True,queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        # self.channel.basic_publish(exchange='',
        #                            routing_key='rpc_queue',
        #                            properties=pika.BasicProperties(
        #                                  reply_to = self.callback_queue,
        #                                  correlation_id = self.corr_id,
        #                                  ),
        #                            body=json.dumps(n))
        # while self.response is None:
        #     self.connection.process_data_events()
        # return json.loads(self.response)
        message = {}
        print "--------------pubnub------------------"
        urllib.urlopen("http://pubsub.pubnub.com/publish/" + settings.PUBNUB_PUB + "/" + settings.PUBNUB_SUB + "/0/rpc_queue/0/" + json.dumps(n))


    def start(self, auctionId, params={}):
        self.send({'auctionId':auctionId, 'method':'start', 'params':params})

    def bid(self, auctionId, params={}):
        self.send({'auctionId':auctionId, 'method':'bid', 'params':params})

    def pause(self, auctionId, params={}):
        self.send({'auctionId':auctionId, 'method':'pause', 'params':params})

    def resume(self, auctionId):
        self.send({'auctionId':auctionId, 'method':'resume', 'params':{}})

    def finish(self, auctionId):
        self.send({'auctionId':auctionId, 'method':'finish', 'params':{}})

    def imAlive(self):
        self.send({'auctionId':0, 'method':'IM_ALIVE', 'params':{}})


bidServerClient = BidServerClient()



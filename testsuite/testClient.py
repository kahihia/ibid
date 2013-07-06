from django.conf import settings
import json
import urllib
import threading

#    'precap': 0,
#    'waiting': 1,
#    'processing': 2,
#    'pause': 2,
#    'waiting_payment': 4,
#    'paid': 5

class TestClient(object):
    def __init__(self, auctionId):
        self.auctionId = auctionId

    def someoneClaimed(self, lastClaimer):
        tmp = {}
        tmp['id'] = self.auctionId
        tmp['price'] = 10
        tmp['timeleft'] = 10
        tmp['lastClaimer'] = lastClaimer
        tmp['facebook_id'] = 0

        result = {'method': 'someoneClaimed', 'data': tmp}
        self._send(result)

    def updatePrecap(self, status):
        tmp = {}
        if status == 'precap':
            tmp['id'] = self.auctionId
            tmp['completion'] = 100
            tmp['bidders'] = 5
        else:
            tmp['completion'] = 100
            tmp['bidders'] = 99
            tmp['id'] = 6

        nresult = {'method': 'updateAuction', 'data': tmp}
        self._send(nresult)

    def auctionAwait(self):
        tmp = {}
        tmp['id'] = self.auctionId
        tmp['status'] = 'waiting'

        result = {'method': 'updateAuction', 'data': tmp}
        self._send(result)

    def auctionActive(self):
        tmp={}
        tmp['id'] = self.auctionId
        tmp['status'] = 'processing'
        tmp['timeleft'] = 30
        tmp['lastClaimer'] = 'Nobody'

        result = {'method': 'updateAuction', 'data': tmp}
        self._send(result)

    def auctionFinish(self):
        tmp={}
        tmp['id'] = self.auctionId
        tmp['status'] = 'waiting_payment'
        tmp['winner'] = "some guy"

        result = {'method': 'updateAuction', 'data': tmp}
        self._send(result)

    def auctionPause(self):
        tmp={}
        tmp['id'] = self.auctionId
        tmp['status'] = 'pause'

        result = {'method': 'updateAuction', 'data': tmp}
        self._send(result)

    def auctionResume(self):
        tmp={}
        tmp['id'] = self.auctionId
        tmp['status'] = 'processing'
        tmp['timeleft'] = 45

        result = {'method': 'updateAuction', 'data': tmp}
        self._send(result)


    def _send(self, message):
        urllib.urlopen("http://pubsub.pubnub.com/publish/" + settings.PUBNUB_PUB + "/" + settings.PUBNUB_SUB + "/0/%2Ftopic%2Fmain%2F/0/" + json.dumps(message))


#tc = TestClient(1)

import simplejson, datetime
class TestMatrix(object):
    def __init__(self, auctionId, data = {"pubnubMessages":[]}):
        self.auctionId = auctionId
        if type(data) == type(''):
            self.data = simplejson.loads(data)['pubnubMessages']
        else:
            self.data = data['pubnubMessages']

        self.TIME = 0
        self.MESSAGE = 1

        self.startingDate = self._toDatetime(self.data[0][self.TIME])
        for i, j in enumerate(self.data):
            #set the time in convenient format
            self.data[i][self.TIME] = self._toDatetime(self.data[i][self.TIME]) - self.startingDate
            #set the auctionId
            if 'id' in self.data[i][self.MESSAGE]['data']:
                self.data[i][self.MESSAGE]['data']['id'] = self.auctionId

    def _toDatetime(self, a):
        return datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S.%f')

    def start(self):
        true = True
        startProcDate = datetime.datetime.now()
        while true:
            if self.data[0][self.TIME] < datetime.datetime.now() - startProcDate:
                print "send pubnub:", self.data[0][self.MESSAGE]
                self._send(self.data[0][self.MESSAGE])
                del self.data[0]

    def _send(self, message):
        urllib.urlopen()

        args = ["http://pubsub.pubnub.com/publish/" + settings.PUBNUB_PUB + "/" + settings.PUBNUB_SUB + "/0/%2Ftopic%2Fmain%2F/0/" + json.dumps(message)]

        th = threading.Thread(target=urllib.urlopen, args=args)
        th.start()


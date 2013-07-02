# Create your views here.
from django.conf import settings
from django.http import HttpResponse
from threading import Timer
import urllib, urllib2
import json

def api(request, method ):
    """API call"""
    return API[method](request)

def startCountDown(request):
    """
    process countdown to start the auction
    """
    #receive parameter
    auctionId = int(request.GET.get('auctionId'))
    bidNumber = int(request.GET.get('bidNumber'))
    time = float(request.GET.get('time', 0))
    kwargs = {'auctionId': auctionId,
              'bidNumber': bidNumber,
              'time': time}

    print "startCountDown",kwargs

    #function to be called on timeout
    def start(**kwargs):
        #if status in precap, paused
        # change status to processing
        print "startCountDown executed ",kwargs
        urllib2.urlopen(settings.BID_SERVICE + 'start/?%s' % urllib.urlencode(kwargs))

    #start countdown
    t = Timer(time, start, kwargs=kwargs)
    t.start()

    #return
    return HttpResponse(json.dumps({'everyThingIsFine':True}))

def stopCountDown(request):
    """
    process countdown to stop the auction
    """
    #receive parameter
    auctionId = int(request.GET.get('auctionId'))
    bidNumber = int(request.GET.get('bidNumber'))
    time = float(request.GET.get('time', 0))
    kwargs = {'auctionId': auctionId,
              'bidNumber': bidNumber,
              'time': time}

    print "stopCountDown",kwargs
    #function to be called on timeout
    def stop(**kwargs):
        #if status == processing
        #and bidNumber is the last
        # change status to finished
        print "stopCountDown executed ",kwargs
        urllib2.urlopen(settings.BID_SERVICE + 'finish/?%s' % urllib.urlencode(kwargs))

    #start countdown
    t = Timer(time, stop, kwargs=kwargs)
    t.start()

    #return
    return HttpResponse(json.dumps({'everyThingIsFine':True}))

API = {
    'stopCountDown': stopCountDown,
    'startCountDown': startCountDown,
}

# -*- coding: utf-8 -*-
import urllib, urllib2
#from django.config import settings
import settings

def delayStart(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'start', 'params':params})
    print "client delayStart", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'startCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'startCountDown/?%s' % urllib.urlencode(kwargs))

def bid(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'bid', 'params':params})
    print "client bid", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'stopCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))

def delayResume(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'pause', 'params':params})
    print "client delayResume", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'startCountDown/?%s' % urllib.urlencode(kwargs))

def delayStop(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'bid', 'params':params})
    print "client delayStop", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    print settings.COUNTDOWN_SERVICE + 'stopCountDown/' + "?" + urllib.urlencode(kwargs)
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))

def resume(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'resume', 'params':{}})
    print "client resume", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.COUNTDOWN_SERVICE + 'stopCountDown/?%s' % urllib.urlencode(kwargs))

def finish(auctionId, bidNumber, time):
    #self.send({'auctionId':auctionId, 'method':'finish', 'params':{}})
    print "client finish", auctionId, bidNumber, time
    kwargs = {
        'auctionId': auctionId,
        'bidNumber': bidNumber,
        'time': time
    }
    urllib2.urlopen(settings.BID_SERVICE + 'finish/?%s' % urllib.urlencode(kwargs))


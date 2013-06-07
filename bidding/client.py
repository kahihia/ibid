# -*- coding: utf8 -*-
from django.conf import settings

'''
Function shortcuts for auction messages.
'''
from django.template.loader import render_to_string
from django.utils import simplejson as json

from lib import stomp
import models

from Pubnub import Pubnub
pubnub = Pubnub( settings.PUBNUB_PUB, settings.PUBNUB_SUB, settings.PUBNUB_SECRET, False)


def send_multiple_messages(pairs):

    from lib import stomp

    # conn = stomp.Connection([('localhost', settings.STOMP_PORT)])
    # conn.start()
    # conn.connect(wait=True)

    for message, destination in pairs:
        #conn.send(message, destination=destination)
        #print 'pubnub ', {'channel': destination, 'message': message}
        #pubnub.publish({'channel': '/topic/main/', 'message': message})
        info = pubnub.publish({
               'channel' : '/topic/main/',
               'message' : message
           })
        print(info)






def send_stomp_message(message, destination):
    send_multiple_messages([(message, destination)])

def auction_created(auction):
    """advice users that a new auction was created"""
    
    messages = []
    
    tmp = {}

    tmp['bidType'] = auction.bid_type

    tmp['id'] = auction.id
    tmp['playFor'] = {'bid':'ITEMS' ,'token':'TOKENS'}[auction.bid_type]
    tmp['completion'] = auction.completion()
    tmp['status'] = auction.status
    tmp['itemName'] = auction.item.name
    tmp['retailPrice'] = str(auction.item.retail_price)
    tmp['completion'] = auction.completion()
    #tmp['placed'] = 9999
    #tmp['bids'] = 9999
    tmp['itemImage'] = auction.item.get_thumbnail()
    tmp['bidders'] = auction.bidders.count()

    result = {'method': 'appendAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')




def updatePrecap(auction):
    """ send messages to update the auction.
    in this step the message receptors only could have the auction in precap or processing."""
    
    tmp = {}
    if auction.status == 'precap':
        tmp['id'] = auction.id
        tmp['completion'] = auction.completion()
        tmp['bidders'] = auction.bidders.count()
    else:
        tmp['completion'] = 100
        tmp['bidders'] = auction.bidders.count()
        tmp['id'] = auction.id
        
    
    #result = {'auction_id': auction.id, 'method': 'updatePrecap', 'params': tmp}
    #send_stomp_message(json.dumps(nresult), '/topic/auction/%d/' % auction.id)
    nresult = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(nresult, '/topic/main/')

    #result = {'auction_id': auction.id, 'time': auction.get_time_left()}
    #send_stomp_message(json.dumps(['time', result]), '/topic/auction/')


def auctionAwait(auction):
    tmp = {}
    tmp['id'] = auction.id
    tmp['status'] = auction.status

    result = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')


def auctionActive(auction):

    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['timeleft'] = auction.get_time_left()
    tmp['lastClaimer'] = 'Nobody'

    result = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')


def auctionFinish(auction):

    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['winner'] = auction.winner.get_profile().display_name()

    result = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')

def auctionPause(auction):

    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status

    result = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')

def auctionResume(auction):

    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['timeleft'] = auction.get_time_left()

    result = {'method': 'updateAuction', 'data': tmp}
    send_stomp_message(result, '/topic/main/')

def someoneClaimed(auction):
    tmp = {}
    tmp['id'] = auction.id
    tmp['price'] = str(auction.price())
    tmp['timeleft'] = auction.get_time_left()
    tmp['lastClaimer'] = auction.get_last_bidder().display_name()
    tmp['facebook_id'] = auction.get_last_bidder().facebook_id

    result = {'method': 'someoneClaimed', 'data': tmp}
    send_stomp_message(result, '/topic/main/')






def do_send_auctioneer_message(auction,message):
    print "do_send_auctioneer_message",auction,message
    text = message.format_message()

    tmp = {}

    tmp['auctioneerMessages'] = [{'text':text,
        'date': message.get_time()
        }]
    tmp['id'] = auction.id

    result = {'method':'receiveAuctioneerMessage', 'data': tmp}
    send_stomp_message(result, '/topic/main/')


def do_send_chat_message(auction, message):
    
    #from routines.templatetags.routines_tags import truncatechars
    #result = {'chat_message': escape(message.text),
    # We mark the message escape when getting it from user
    text = message.format_message()
    tmp = {'user_name':message.user.display_name(),
        'user_pic':message.user.picture(),
        'message':text,
        'user_link': message.user.user_link(), 
        'date': message.get_time()
        }
          
    #tmp = {'chat_message': text,
    #          'username':message.user.display_name(),
    #          'user_link' : message.user.user_link(),
    #          'auction': message.auction.id, 
    #          'time':message.get_time(), 
    #          'avatar':message.user.picture()}
              
    result = {'auction_id': auction.id, 'method': 'addChatMessage', 'params': tmp}
    send_stomp_message(json.dumps(result), '/topic/auction/%d/'%auction.id )






def log(text):
    result = {'method': 'log', 'params': 'SERVER: '+repr(text)}
    send_stomp_message(json.dumps(result), '/topic/main/' )

def callReverse(userIdentifier, function):
    result = {'method': 'callReverse', 'params': {'userIdentifier':userIdentifier, 'function': function}}
    send_stomp_message(json.dumps(result), '/topic/main/' )

    

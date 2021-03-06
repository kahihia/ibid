# -*- coding: utf8 -*-
from datetime import datetime
import logging
import threading
import time

from django.conf import settings

from lib.Pubnub import Pubnub


logger = logging.getLogger('django')
pubnub = Pubnub( settings.PUBNUB_PUB, settings.PUBNUB_SUB, settings.PUBNUB_SECRET, False)


def send_multiple_messages(pairs):
    for message, destination in pairs:
        send_pubnub_message(message, destination)


def send_pubnub_message(message, destination):
    if type(message) is dict:
        message['timestamp'] = time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime())
    
    info = pubnub.publish({
           'channel' : destination,
           'message' : [message]
       })
    if info[0]==0:
        time.sleep(5) # delays for 5 seconds
        info = pubnub.publish({
           'channel' : destination,
           'message' : [message]
        })
        if info[0]==0:
            logger.warn("Couldn't send message, connection lost.")  
    

def _send_pubnub_message(message, destination):
   
    if type(message) is dict:
        message['timestamp'] = time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime())

    ## non threaded
    info = pubnub.publish({
           'channel' : destination,
           'message' : message
       })
    if info[0]==0:
        time.sleep(5)
        info = pubnub.publish({
           'channel' : destination,
           'message' : message
        })
        if info[0]==0:
            logger.warn("Couldn't send message, connection lost.")  


def sendPackedMessages(clientMessages):
    #group messages of the same channel
    tmp = {}

    for message, channel in clientMessages:
        if channel not in tmp.keys():
            tmp[channel] = []
        tmp[channel].append(message)

    for key in tmp.keys():
        _send_pubnub_message(tmp[key], key)


def auction_created(auction):
    tmp = {}

    tmp['id'] = auction.id
    tmp['playFor'] = {'bid':'credit' ,'token':'token'}[auction.bid_type]
    tmp['completion'] = auction.completion()
    tmp['status'] = auction.status
    if auction.bid_type == 'bid':
        tmp['bidType'] = 'credit'
    elif auction.bid_type == 'token':
        tmp['bidType'] = 'token'

    tmp['bidPrice'] = auction.minimum_precap
    tmp['itemName'] = auction.item.name
    tmp['retailPrice'] = str(auction.item.retail_price)
    tmp['completion'] = auction.completion()
    tmp['itemImage'] = auction.item.get_thumbnail()
    tmp['itemDescription'] = auction.item.description
    tmp['bidders'] = auction.bidders.count()
    tmp['placed'] = 0
    tmp['timeleft'] = None
    tmp['bidNumber'] = 0
    tmp['bids'] = 0
    tmp['auctioneerMessages'] = []
    tmp['chatMessages'] = []


    result = {'method': 'appendAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def updatePrecap(auction):
    tmp = {}
    if auction.status == 'precap':
        tmp['id'] = auction.id
        tmp['completion'] = auction.completion()
        tmp['bidders'] = auction.bidders.count()
    else:
        tmp['completion'] = 100
        tmp['bidders'] = auction.bidders.count()
        tmp['id'] = auction.id
        
    nresult = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(nresult, '/topic/main/')


def updatePrecapMessage(auction):
    tmp = {}
    if auction.status == 'precap':
        tmp['id'] = auction.id
        tmp['completion'] = auction.completion()
        tmp['bidders'] = auction.bidders.count()
    else:
        tmp['completion'] = 100
        tmp['bidders'] = auction.bidders.count()
        tmp['id'] = auction.id

    nresult = {'method': 'updateAuction', 'data': tmp}
    return (nresult, '/topic/main/')


def auctionAwait(auction):
    tmp = {}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    if auction.bid_type == 'token':
        tmp['startDate'] = 'SYNCING...'
    else:
        tmp['startDate'] = auction.start_date.strftime('%B %d - %H:%M')

    result = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def auctionActive(auction):

    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['timeleft'] = auction.get_time_left()
    tmp['lastClaimer'] = 'Nobody'

    result = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def auctionFinish(auction):
    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['winner'] = {'firstName': auction.winner.first_name if auction.winner else 'Nobody has bid!',
                     'displayName': auction.winner.display_name() if auction.winner else 'Nobody',
                     'id': auction.winner.id if auction.winner else '',
                     'facebookId': auction.winner.facebook_id if auction.winner else ''}
    tmp['won_price'] = str(auction.won_price)
    
    result = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def auctionPause(auction):
    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status

    result = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def auctionResume(auction):
    tmp={}
    tmp['id'] = auction.id
    tmp['status'] = auction.status
    tmp['timeleft'] = auction.get_time_left()

    result = {'method': 'updateAuction', 'data': tmp}
    send_pubnub_message(result, '/topic/main/')


def someoneClaimed(auction):
    tmp = {}
    tmp['id'] = auction.id
    tmp['price'] = str(auction.price())
    tmp['timeleft'] = auction.get_time_left()
    tmp['lastClaimer'] = auction.get_last_bidder().display_name()
    tmp['facebook_id'] = auction.get_last_bidder().facebook_id
    tmp['user'] = {'firstName': auction.get_last_bidder().first_name,
                     'displayName': auction.get_last_bidder().display_name(),
                     'facebookId': auction.get_last_bidder().facebook_id}
    tmp['bidNumber'] = auction.used_bids()/auction.minimum_precap

    result = {'method': 'someoneClaimed', 'data': tmp}
    send_pubnub_message(result, '/topic/main/%s' % auction.id)


def someoneClaimedMessage(auction):
    tmp = {}
    tmp['id'] = auction.id
    tmp['price'] = str(auction.price())
    tmp['timeleft'] = auction.get_time_left()
    tmp['lastClaimer'] = auction.get_last_bidder().display_name()
    tmp['facebook_id'] = auction.get_last_bidder().facebook_id
    tmp['user'] = {'firstName': auction.get_last_bidder().first_name,
                     'displayName': auction.get_last_bidder().display_name(),
                     'facebookId': auction.get_last_bidder().facebook_id}
    tmp['bidNumber'] = auction.used_bids()/auction.minimum_precap
    tmp['timestamp'] = time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime())

    result = {'method': 'someoneClaimed', 'data': tmp}
    return (result, '/topic/main/%s' % auction.id)


def do_send_auctioneer_message(auction,message):
    text = message.format_message()
    tmp = {}
    tmp['auctioneerMessages'] = [{'text':text,'date': message.get_time()}]
    tmp['id'] = auction.id

    result = {'method':'receiveAuctioneerMessage', 'data': tmp}
    send_pubnub_message(result, '/topic/main/%s' % auction.id)


def do_send_chat_message(auction, message):
    text = message.format_message()
    user = {}
    user['displayName'] = message.get_user().display_name()
    user['profileFotoLink'] = message.get_user().picture()
    user['profileLink'] = message.get_user().user_link()
    user['facebookId'] = message.get_user().user_facebook_id()
    result = {'method':'receiveChatMessage', 'data':{'id':auction.id, 'user': user, 'text': text}}
    send_pubnub_message(result, '/topic/chat/%s' % auction.id)


def do_send_global_chat_message(member, text):

    user = {}
    user['displayName'] = member.first_name
    user['profileFotoLink'] = "http://graph.facebook.com/%s/picture" % str(member.facebook_id)
    user['profileLink'] = "https://facebook.com/%s" % str(member.facebook_id)
    user['facebookId'] = member.facebook_id
    result = {'method':'receiveChatMessage', 'data':{'user': user, 'text': text}}
    send_pubnub_message(result, 'global')


def log(text):
    result = {'method': 'log', 'params': 'SERVER: '+repr(text)}
    send_pubnub_message(result, '/topic/main/' )


def callReverse(userIdentifier, function):
    result = {'method': 'callReverse', 'params': {'userIdentifier':userIdentifier, 'function': function}}
    send_pubnub_message(result, '/topic/main/' )


def update_credits(member):
    tmp = {}
    tmp['credits'] = member.bids_left
    send_pubnub_message({'method': 'update_credits','data':tmp}, '/topic/main/%s' % member.id)

def update_tokens(member):
    tmp = {}
    tmp['tokens'] = member.tokens_left
    send_pubnub_message({'method': 'update_tokens','data':tmp}, '/topic/main/%s' % member.id)

def clock_pubnub():
    message = {}
    message['timestamp'] = time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime())
    send_pubnub_message({'data':message}, '/topic/main/clock/')

   


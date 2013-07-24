# -*- coding: utf8 -*-
from django.conf import settings
import threading
from datetime import datetime

from Pubnub import Pubnub
pubnub = Pubnub( settings.PUBNUB_PUB, settings.PUBNUB_SUB, settings.PUBNUB_SECRET, False)


def send_multiple_messages(pairs):
    for message, destination in pairs:
        send_pubnub_message(message, destination)


def send_pubnub_message(message, destination):
    if type(message) is dict:
        message['timestamp'] = str(datetime.now())
    info = pubnub.publish({
           'channel' : destination,
           'message' : [message]
       })

def _send_pubnub_message(message, destination):

    if type(message) is dict:
        message['timestamp'] = str(datetime.now())

    ## threaded
    #th = threading.Thread(target=pubnub.publish, args=[{
    #      'channel' : destination,
    #       'message' : message
    #   }])
    #th.start()

    ## non threaded
    info = pubnub.publish({
           'channel' : destination,
           'message' : message
       })
    #print(info)

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
    tmp['bidders'] = auction.bidders.count()

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
    tmp['winner'] = {'firstName': auction.winner.get_profile().user.first_name if auction.winner else 'Nobody has bid!',
                     'displayName': auction.winner.get_profile().display_name() if auction.winner else 'Nobody',
                     'facebookId': auction.winner.get_profile().facebook_id if auction.winner else ''}

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
    tmp['user'] = {'firstName': auction.get_last_bidder().user.first_name,
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
    tmp['user'] = {'firstName': auction.get_last_bidder().user.first_name,
                     'displayName': auction.get_last_bidder().display_name(),
                     'facebookId': auction.get_last_bidder().facebook_id}
    tmp['bidNumber'] = auction.used_bids()/auction.minimum_precap

    result = {'method': 'someoneClaimed', 'data': tmp}
    return (result, '/topic/main/%s' % auction.id)

def do_send_auctioneer_message(auction,message):
    text = message.format_message()

    tmp = {}

    tmp['auctioneerMessages'] = [{'text':text,
        'date': message.get_time()
        }]
    tmp['id'] = auction.id

    result = {'method':'receiveAuctioneerMessage', 'data': tmp}
    send_pubnub_message(result, '/topic/main/%s' % auction.id)

def do_send_chat_message(auction, message):
    text = message.format_message()

    user = {}
    user['displayName'] = message.user.display_name()
    user['profileFotoLink'] = message.user.picture()
    user['profileLink'] = message.user.user_link()
    user['tokens'] = 0
    user['credits'] = 0

    result = {'method':'receiveChatMessage', 'data':{'id':auction.id, 'user': user, 'text': text}}

    send_pubnub_message(result, '/topic/chat/%s' % auction.id)

def log(text):
    result = {'method': 'log', 'params': 'SERVER: '+repr(text)}
    send_pubnub_message(result, '/topic/main/' )

def callReverse(userIdentifier, function):
    result = {'method': 'callReverse', 'params': {'userIdentifier':userIdentifier, 'function': function}}
    send_pubnub_message(result, '/topic/main/' )

    

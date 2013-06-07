# -*- coding: utf8 -*-
from django.conf import settings

'''
Function shortcuts for auction messages.
'''
from django.template.loader import render_to_string
from django.utils import simplejson as json
#import simplejson as json

def send_multiple_messages(pairs):
    from lib import stomp
    conn = stomp.Connection([('localhost', settings.STOMP_PORT)])
    conn.start()
    conn.connect(wait=True)
    for message, destination in pairs:
        conn.send(message, destination=destination)
    conn.disconnect()

def send_stomp_message(message, destination):
    send_multiple_messages([(message, destination)])

auction_templates = {'precap' : 'bidding/auctions/auction_precap.html',
                     'waiting' : 'bidding/auctions/auction_waiting.html',
                     'processing' : 'bidding/auctions/auction_running.html',
                     'waiting_payment' : 'bidding/auctions/auction_finished.html',
                     'pause' : 'bidding/auctions/auction_paused.html'}

#TODO see if member info can be separated to other function
def render_auction(auction, member=None):
    bids_left = None
    if member:
        bids_left = member.auction_bids_left(auction)
    
    response = render_to_string(auction_templates[auction.status], 
                                {'auction':auction, 'left' : bids_left})
    return {'auction_id': auction.id, 'content' : response}

detail_templates = {'precap' : 'bidding/detail/detail_precap.html',
                     'waiting' : 'bidding/detail/detail_waiting.html',
                     'processing' : 'bidding/detail/detail_running.html',
                     'waiting_payment' : 'bidding/detail/detail_finished.html',
                     'paid' : 'bidding/detail/detail_finished.html',
                     'pause' : 'bidding/detail/detail_paused.html'}

def render_details(auction):
    return {'content' : render_to_string(detail_templates[auction.status], 
                                {'auction':auction,}),
            'status' : auction.status}

#def send_member_joined(auction, member):
#    data = {'user_id' : member.id,
#            'user_name': member.display_name(),
#            'user_link': member.facebook_profile_url,
#            'avatar': member.display_picture()}
#    message = json.dumps(['join', data])
#    send_stomp_message(message, '/topic/detail/%d/' % auction.id)

def send_member_left(auction, member):
    data = {'user_id' : member.id,}
    message = json.dumps(['leave', data])
    send_stomp_message(message, '/topic/detail/%d/' % auction.id)


    
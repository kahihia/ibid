# -*- coding: utf-8 -*-

""" Client library to track events metrics """

from mixpanel import Mixpanel


_MP = None


def initialize(mp_token):
    global _MP
    if _MP is None:
        _MP = Mixpanel(mp_token)


def track_event(user_id, event, data):
    global _MP
    _MP.track(user_id, event, data)


def join_auction(user, auction):
    _update_user_profile(user)
    _track_auction_event(user.id, auction, 'JoinAuction')


def add_bids(user, auction):
    _track_auction_event(user.id, auction, 'AddBids')


def rem_bids(user, auction):
    _track_auction_event(user.id, auction, 'RemBids')


def claim_auction(user, auction):
    _track_auction_event(user.id, auction, 'ClaimAuction')


def win_auction(user, auction):
    _track_auction_event(user.id, auction, 'WinAuction')


def leave_auction(user, auction):
    _track_auction_event(user.id, auction, 'LeaveAuction')


def _track_auction_event(user_id, auction, event):
    data = _get_auction_data(auction)
    track_event(user_id, event, data)



def _update_user_profile(user):
    global _MP
    _MP.people_set(user.id, {
        '$first_name': user.first_name,
        '$last_name': user.last_name,
        '$email': user.email,
    })


def _get_auction_data(auction):
    data = {
        'auction_id': auction.id,
        'auction_type': auction.bid_type,
        'item_id': auction.item.id,
        'item_name': auction.item.name,
        #'item_categories': auction.item.categories,
    }
    return data

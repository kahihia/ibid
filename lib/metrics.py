# -*- coding: utf-8 -*-

""" Client library to track events metrics """

from mixpanel import Mixpanel


_MP = None


def initialize(mp_token):
    global _MP
    if _MP is None:
        _MP = Mixpanel(mp_token)


def track_event(user, event, data):
    global _MP
    _MP.track(user, event, data)



if __name__ == '__main__':
    token = 'baff1480b94c0f1acbf6fe1249ee35de'  # My New Project
    initialize(token)
    user = 3
    data = {
        'auction_type': 'Token',
        'auction_id': 1,
        'auction_category': 'electronics',
        'app_version': 'ios',
    }
    track_event(user, 'startBiddding', data)
    track_event(user, 'startBiddding', data)

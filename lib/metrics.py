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

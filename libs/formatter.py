# -*- coding: utf-8 -*-

import datetime
import decimal


def flatten(a):
    """Flattens the given object. So far accepts dict, list, string, datetime and
    decimal"""
    if isinstance(a, dict):
        a = flatten_dict(a)
    elif isinstance(a, list):
        a = flatten_list(a)
    elif isinstance(a, datetime.datetime):
        a = a.isoformat()
    elif isinstance(a, decimal.Decimal):
        a = str(a)
    return a


def flatten_dict(a):
    """Flattens the given dict"""
    res = {}
    for k, v in a.iteritems():
        res[k] = flatten(v)
    return res


def flatten_list(a):
    """Flattens the given list"""
    res = []
    for v in a:
        res.append(flatten(v))
    return res


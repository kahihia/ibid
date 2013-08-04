# -*- coding: utf-8 -*-
"""
value_objects are objects with no methods, only properties. They serializable to JSON or any other serial method.
Multilingual, platform agnostic and provide a strict standard message for the whole platform.

Here are listed the value objects needed to run auctions and manage profiles, particularly everything that needs to go
out of the server has to have a value object defined here.

Messages are also documented here:
https://github.com/dnuske/ibiddjango/wiki/Message-objects

"""
__author__ = 'dnuske'
__date__ = '2013-07-31'

import json
import datetime
from time import mktime


class ValueObject(dict):
    def __init__(self):
        pass

    def toJson(self):
        return json.dumps(self, cls = DatatimeEncoder)

class LoggedInUser(ValueObject):
    def __init__(self, id = "", name = "", link = "", pictureUrl = "", credits = 0, tokens = 0):
        self['id'] = id
        self['name'] = name
        self['link'] = link
        self['pictureUrl'] = pictureUrl
        self['credits'] = credits
        self['tokens'] = tokens


class User(ValueObject):
    def __init__(self, id = 0,name = "",link = "",pictureUrl = ""):
        self["id"] = id
        self["name"] = name
        self["link"] = link
        self["pictureUrl"] = pictureUrl


class FriendInvitationAccepted(ValueObject):
    def __init__(self, prize = 0,user = None):
        self["prize"] = prize
        self["user"] = user


class Auction(ValueObject):
   def __init__(self, completion = 0, status = "", itemImage = "", chatMessages = [], retailPrice = "0.00", bidders = 0, itemName = "", id = 0, auctioneerMessages = [], winner = '', timeleft = 0, bidNumber = 0, bids = 0, placed = 0, mine=False, bidPrice=0, bidType=''):
        self["completion"] = completion
        self["status"] = status
        self["itemImage"] = itemImage
        self["chatMessages"] = chatMessages
        self["retailPrice"] = retailPrice
        self["bidders"] = bidders
        self["itemName"] = itemName
        self["id"] = id
        self["auctioneerMessages"] = auctioneerMessages
        self["winner"] = winner
        self["timeleft"] = timeleft
        self["bidNumber"] = bidNumber
        self["bids"] = bids
        self["placed"] = placed
        self["mine"] = mine
        self["bidPrice"] = bidPrice
        self["bidType"] = bidType


class ChatMessage(ValueObject):
    def __init__(self, date = "",text = "",user = "",auctionId = 0):
        self["date"] = date
        self["text"] = text
        self["user"] = user
        self["auctionId"] = auctionId


class AuctioneerMessage(ValueObject):
    def __init__(self, date = "", text = "", auctionId = 0):
        self["date"] = date
        self["text"] = text
        self["auctionId"] = auctionId


class Event(ValueObject):
    """
    If objects were mythology entities this would be Zeus.
    """
    def __init__(self, event = "",  data = "", sender = "", receiver = "", transport = "", timestamp = "", id = None):
        """
        parameters:
         * event: The object and his event name as string. Ex.: 'main:invitationAccepted'
         * data: Event data. Could be object, null, string or int, as long as the event receptor know what to expect and how to use it. This field fits the requirements to be filled with object messages
         * sender: Could be 'server-'+serverName if event origin is server or 'client-'+clientId if the origin is the client. Ex.: 'server-coconut-master' or 'client-212156'
         * receiver: Same value rule as server. Except 'server' is wildcard for load balancer.
         * transport: This keyword will indicate the mechanism to implement in order to receive the event.
            - pubnub: The message has arrived from pubnub, just interpret it.
            - request: The message has arrived in a request call back, just interpret it.
            - combined: The message that has arrived to the client indicates that the content should be requested via http request to API calling method 'combined'.
         * timestamp: The current timestamp
         * id: The event sender must have an id generator (usually a counter) to keep record of the event message, to store and tracking. For the server this can be database driven, and for the client, the last used id could be asked to the backend and continue the count from then.
        """
        self['event'] = event
        self['data'] = data
        self['sender'] = sender
        self['receiver'] = receiver
        self['transport'] = transport
        self['timestamp'] = timestamp
        self['id'] = id

    class TRANSPORT:
        PUBNUB = 'pubnub'
        REQUEST = 'request'
        COMBINED = 'combined'

    class SENDER:
        SERVER = 'server'

    class RECEIVER:
        CLIENT_FB = 'client-fb-'

    class EVENT:
        MAIN__LOAD_USER_DETAILS =           'main:loadUserDetails'
        MAIN__LOAD_AUCTIONS =               'main:loadAuctions'
        MAIN__FRIEND_INVITATION_ACCEPTED =  'main:friendInvitationAccepted'

class EventList(list):
    def __init__(self, *args):
        for arg in args:
            self.append(arg)

    def toJson(self):
        return json.dumps(self, cls = DatatimeEncoder)



class DatatimeEncoder(json.JSONEncoder):
    """
    so json encodes datatime
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)



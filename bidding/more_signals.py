# -*- coding: utf-8 -*-
import logging

import json
from django.db.models.signals import post_save
from django.dispatch.dispatcher import Signal
from django_facebook import signals
from django_facebook.utils import get_user_model

from bidding.models import Auction
from bidding.models import ConfigKey
from bidding.models import Invitation
import client
import message.value_objects as vo
import message.value_objects_factory as vo_factory


logger = logging.getLogger('django')

precap_finished_signal = Signal(providing_args=["auction"])


def auctionCreated(**kwargs):
    if 'created' in kwargs and kwargs['created']:
        auction = kwargs.get('instance')
        client.auction_created(auction)        

post_save.connect(auctionCreated, Auction)


def fb_user_registered_handler(sender, user, facebook_data, **kwargs):
    logger.debug('fb_user_registered_handler')
    member = user
    member.bids_left = 0
    member.tokens_left = 2000
    member.save()
    #was this user invited?
    userList = Invitation.objects.filter(invited_facebook_id=facebook_data['facebook_id'])
    if len(userList):
        invited = userList[0]
        prize = ConfigKey.get('INVITE_FRIENDS_TOKEN_PRIZE', 1000)
        invited.inviter.tokens_left += prize
        invited.inviter.save()
        tmp = {}
        tmp['invited_name'] = member.display_name()
        Notification.objects.create(recipient=invited.inviter, sender=None, notification_type='FriendJoined', message=json.dumps(tmp))
        client.update_tokens(member)


        #add an event to the inviter, to show it the next time he logs in
        #TODO: change this to transport pubnub
        eventFriendInvitationAccepted = vo_factory.create_voFriendInvitationAccepted(prize, [])
        eventFriendInvitationAccepted['users'] = [vo.User( facebook_data['facebook_id'],facebook_data['facebook_name'],"http://facebook.com/%s"%str(facebook_data['facebook_id']) , facebook_data['image_thumb'])]
        eventList = vo.EventList()
        eventList.append(eventFriendInvitationAccepted)

        invited.inviter.setSession('event',eventList)

signals.facebook_user_registered.connect(fb_user_registered_handler, sender=get_user_model())

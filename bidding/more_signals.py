# -*- coding: utf-8 -*-

from django.dispatch.dispatcher import receiver, Signal
from django.db.models.signals import post_save
#|from django.db.models import signals

import client

from bidding.models import Auction, Invitation, ConfigKey
import message.value_objects as vo
import message.value_objects_factory as vo_factory
from django.contrib.auth.models import User
from django_facebook.utils import get_user_model

from django_facebook import signals
import logging

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

    #rint eventFriendInvitationAccepted

    if len(userList):
        invited = userList[0]
        prize = ConfigKey.get('INVITE_FRIENDS_TOKEN_PRIZE', 1000)
        invited.inviter.tokens_left += prize
        invited.inviter.save()

        #add an event to the inviter, to show it the next time he logs in
        #TODO: change this to transport pubnub
        eventFriendInvitationAccepted = vo_factory.create_voFriendInvitationAccepted(prize, [])
        eventFriendInvitationAccepted['users'] = [vo.User( facebook_data['facebook_id'],facebook_data['facebook_name'],"http://facebook.com/%s"%str(facebook_data['facebook_id']) , facebook_data['image_thumb'])]
        eventList = vo.EventList()
        eventList.append(eventFriendInvitationAccepted)

        invited.inviter.setSession('event',eventList)

signals.facebook_user_registered.connect(fb_user_registered_handler, sender=get_user_model())

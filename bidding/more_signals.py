# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver, Signal
from django_facebook import signals

import message.value_objects as vo
import message.value_objects_factory as vo_factory

import client
from bidding.models import Auction, Invitation, ConfigKey


precap_finished_signal = Signal(providing_args=["auction"])


def auctionCreated(**kwargs):
    if 'created' in kwargs and kwargs['created']:
        auction = kwargs.get('instance')
        client.auction_created(auction)        

post_save.connect(auctionCreated, Auction)


def fb_user_registered_handler(sender, user, facebook_data, **kwargs):
    member = user.get_profile()
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

        #add an event to the inviter, to show it the next time he logs in
        #TODO: change this to transport pubnub
        eventFriendInvitationAccepted = vo_factory.create_voFriendInvitationAccepted(prize, [])
        eventFriendInvitationAccepted['users'] = [vo.User( facebook_data['facebook_id'],facebook_data['facebook_name'],"http://facebook.com/%s"%str(facebook_data['facebook_id']) , facebook_data['image_thumb'])]
        eventList = vo.EventList()
        eventList.append(eventFriendInvitationAccepted)

        invited.inviter.setSession('event',eventList)

signals.facebook_user_registered.connect(fb_user_registered_handler, sender=User)

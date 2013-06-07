# -*- coding: utf-8 -*-

from django.dispatch.dispatcher import receiver, Signal
from django.db.models.signals import post_save
from django.dispatch import dispatcher
from django.db.models import signals

import client
from django.utils import simplejson as json

from bidding.models import Bid, Auction, Invitation

import open_facebook


precap_finished_signal = Signal(providing_args=["auction"])


#@receiver(precap_finished_signal)
def firstBid(sender, **kwargs):
    client.send_stomp_message(json.dumps({'method':'log','params':'SERVER: auctionStarted'}), '/topic/main/')

    auction = kwargs['auction']

    #Auctioneer = AuctioneerProxy() #try instantiate this to put the first bid, didn't work.
    
    b = Bid(auction=auction, unixtime = Decimal("%f" % time.time()))
    b.save()

def auctionCreated(**kwargs):
    if 'created' in kwargs and kwargs['created']:
        auction = kwargs.get('instance')
        client.auction_created(auction)        

post_save.connect(auctionCreated, Auction)




from django.contrib.auth.models import User
from django_facebook import signals
from django_facebook.utils import get_profile_class

import urlparse

def fb_user_registered_handler(sender, user, facebook_data, **kwargs):
    member = user.get_profile()
    member.bids_left = 0
    member.tokens_left = 2000
    member.save()

    #was this user invited?
    userList = Invitation.objects.filter(invited_facebook_id=facebook_data['facebook_id'])

    if len(userList):
        invited = userList[0]
        invited.inviter.tokens_left += 1000
        invited.inviter.save()

        actok = urlparse.parse_qs(urlparse.urlsplit(facebook_data['image'])[3])['access_token']
        #check permission
        of = open_facebook.OpenFacebook(actok[0])
        res = of.get('/me/permissions')
        #res = {u'paging': {u'next': u'https://graph.facebook.com/100004432174268/permissions?access_token=AAADmEQx6CoMBACatrXgdjUzxQhzWWOZADs1Age3cyJhaK3V3CW1oz2VeTaeZBpl8rq0ghzwKV1oVpZCf3GnBPJci6ptSWWGTbTqgmvLGAZDZD&limit=5000&offset=5000'}, u'data': [{u'bookmarked': 1, u'publish_actions': 1, u'create_note': 1, u'user_birthday': 1, u'video_upload': 1, u'user_location': 1, u'installed': 1, u'publish_stream': 1, u'photo_upload': 1, u'share_item': 1, u'email': 1, u'status_update': 1}]}
        if 'data' in res and len(res['data']) and 'publish_stream' in res['data'][0] and bool(res['data'][0]['publish_stream']):
            invited.inviter.tokens_left += 500
        invited.inviter.save()

signals.facebook_user_registered.connect(fb_user_registered_handler, sender=User)


#def auction_created(sender, instance, signal, *args, **kwargs):
#    client.log('auction created !!!!')
#    if 'created' in kwargs:
#        if kwargs['created']:
#            client.auction_created(sender)
# Send email
#post_save.connect(auction_created, sender=Auction)


# -*- coding: utf-8 -*-

from datetime import datetime
import uuid
import re

from django.db import models
from django.conf import settings
from django.contrib import auth

from django.conf import settings
from bidding.models import Auction, Member


CHATROOM_STATUS_CHOICES = (
     ('created', 'Created'),
     ('accepted', 'Accepted'),
     ('declined', 'Declined'),
     ('closed', 'Closed'),
)

def get_uuid():
    """
    Returns new UUID as string,
    made to use as a default in model fields
    """
    return str(uuid.uuid4())


class ChatUser(models.Model):
    """
    Separate Chat user object, made to decouple 
    chat and chat messages from Django auth system, 
    and to allow automatic entities to use the chat.
    Avatar should be an absolute URL, or URL relative to the 
    current site root.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    def picture(self):
        """ Returns the chat avatar. """
        return self.user.get_profile().display_picture()
        
    def display_name(self):
        return self.user.get_profile().display_name()
    
    def user_link(self):
        return self.user.get_profile().facebook_profile_url

    def __unicode__(self):
        return self.display_name()

    def can_chat(self, auction):
        """ Returns True if the user can chat in the given auction. """
        member = self.user.get_profile()
        
        return not member.remove_from_chat and auction.has_joined(member)


class AuctioneerProxy(object):
    def picture(self):
        return settings.STATIC_URL + 'images/auctioneer_small.jpg'
        
    def display_name(self):
        return "Auctioneer"
    
    def user_link(self):
        return ""
    
    def __unicode__(self):
        return u'Auctioneer'


class Message(models.Model):
    _user = models.ForeignKey(ChatUser, verbose_name='user', blank=True, null=True)
    text = models.TextField()
    created = models.DateTimeField(default=datetime.now)
    auction = models.ForeignKey(Auction)

    def get_time(self):
        """ Returns time when message was created in the readable form. """
        
        return self.created.strftime("%m/%d/%y %H:%M")
    
    def get_user(self):
        return self._user or AuctioneerProxy()
    
    def set_user(self, user):
        self._user = user

    def format_message(self):
        m = re.search("member:(\d+)", self.text)
        if m:
            member = Member.objects.get(pk=m.group(1))
            text = self.text.replace(m.group(0), "member")
            return text.format(member = member.display_linked_facebook_profile())
        return self.text
        
    user = property(get_user, set_user)
    
    class Meta:
        verbose_name = 'chat message'

class AuctioneerPhrase(models.Model):
    key = models.CharField(max_length=20)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.key

# -*- coding: utf-8 -*-

from datetime import datetime
import re

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


CHATROOM_STATUS_CHOICES = (
     ('created', 'Created'),
     ('accepted', 'Accepted'),
     ('declined', 'Declined'),
     ('closed', 'Closed'),
)


class ChatUser(models.Model):
    """
    Separate Chat user object, made to decouple 
    chat and chat messages from Django auth system, 
    and to allow automatic entities to use the chat.
    Avatar should be an absolute URL, or URL relative to the 
    current site root.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def picture(self):
        """ Returns the chat avatar. """
        return self.content_object.display_picture()
        
    def display_name(self):
     
        return self.content_object.display_name()
    
    def user_link(self):
        return self.content_object.facebook_profile_url

    def user_facebook_id(self):
          return self.content_object.facebook_id

    def __unicode__(self):
        return self.display_name()

    def can_chat(self, auction_id):
        """ Returns True if the user can chat in the given auction. """
        return self.content_object.can_chat(auction_id)


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
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def get_time(self):
        """ Returns time when message was created in the readable form. """
        
        return self.created.strftime("%m/%d/%y %H:%M:%S")

    
    def get_user(self):
        return self._user or AuctioneerProxy()
    
    def set_user(self, user):
        self._user = user

    def format_message(self):
     from bidding.models import  Member
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
    key = models.CharField(max_length=20,unique=True)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.key

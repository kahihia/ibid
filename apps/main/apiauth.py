# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('django')
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.authentication import Authentication
from bidding.models import ConfigKey, Auction

class CustomAuthentication(Authentication):
    
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()
    # Optional but recommended
    def get_identifier(self, request):
        return request.user
    
###########    AUTHORIZATION METHODS TO ENABLE OR DISABLE DATA ACCES FOR A USER   ###########

class NoAuthorization(Authorization):
    
    """
    Is used as a super class to negate most of the hits
    """

    def read_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no lists.")
    def read_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no detail.")
    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

class UserNotificationsAuthorization(ReadOnlyAuthorization):
 
    """
    This class is used to control the access to notifications
    """
    def read_list(self, object_list, bundle):
        
        """
        Checks a configKey to know if the retrieval of notifications
        is enabled
        """
        
        if ConfigKey.get('NOTIFICATIONS_ENABLED', False):
            return object_list.filter(recipient=bundle.request.user, status='Unread')
        raise Unauthorized("Notifications disabled")
    
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.recipient == bundle.request.user
        
    
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user
    
class MemberAuthorization(NoAuthorization):

    def read_list(self, object_list, bundle):
        return object_list
        
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.request.user == bundle.obj
    
    def update_detail(self, object_list, bundle):
        return bundle.request.user == bundle.obj

class MessageAuthorization(NoAuthorization):
    
    def read_list(self, object_list, bundle):
        if object_list:
            if not Auction.objects.get(id=object_list[0].object_id).bidders.filter(id=bundle.request.user.id).exists():
                raise Unauthorized("Not a bidder")
        return object_list
    
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return False
    
    def create_list(self, object_list, bundle):
        if object_list:
            auction_id = int(object_list[0].object_id)
        if bundle.request.user.can_chat(auction_id):
            return object_list
        raise Unauthorized("Can't chat")

    def update_detail(self, object_list, bundle):
        log.debug("update_detail")
        log.debug(bundle.obj)
        if bundle.obj:
            log.debug("dentro del if")
            auction_id = int(bundle.obj.object_id)
            if bundle.request.user.can_chat(auction_id):
                return True
        return False

class PaymentAuthorization(NoAuthorization):
    
    def create_list(self, object_list, bundle):
        if object_list:
            if object_list[0].member == bundle.request.user:
                return object_list
        raise Unauthorized("payment error")


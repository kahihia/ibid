# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('django')

from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized

from bidding.models import ConfigKey


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


class UserNotificationsAuthorization(NoAuthorization):
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
    
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user


class UserByTokenAuthorization(NoAuthorization):
    """
    This authorization class is used to login or sign in and retrieves their details
    """
    def read_detail(self, object_list, bundle):
        return bundle.obj != None


class PlayerActionAuthorization(NoAuthorization):
    """
    Only allows to modify the auction bids if the request user is in the auction.
    If joining an auction, checks that the user has not already joined.
    """    
    def update_detail(self, object_list, bundle):
        
        logger.debug('PLAYER ACTION AUTHORIZATION')
        action=bundle.request.META['REQUEST_URI'].split('/')[-2]
        logger.debug(action)
        
        if action == 'join_auction':
            if bundle.request.user not in bundle.obj.bidders.all():
                return True
            else:
                return False
        return bundle.request.user in bundle.obj.bidders.all()
        
            

class AuctionAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        """
        If querying for a member's auctions, checks that the logged member
        matches the member_id in the url.
        If there's no member_id in the url that means that the request is for
        all auctions so all auctions are allowed.
        """
        method = bundle.request.META['REQUEST_URI'].split('/')[-2]
        
        try:
            object_id = int(bundle.request.META['REQUEST_URI'].split('/')[-1])
        except:    
            return object_list
        if method=='user' or method =='getAuctionsIwon':
           
            if object_id == bundle.request.user.id :    
                    return object_list
            else:    
                raise Unauthorized("Sorry, you're not the user.")    
        else:
            return object_list
         
    def read_detail(self, object_list, bundle):
        return bundle.obj != None
    

class MemberAuthorization(ReadOnlyAuthorization):
    def update_detail(self, object_list, bundle):
        return bundle.request.user.id == bundle.obj.id

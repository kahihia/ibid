# -*- coding: utf-8 -*-
from django.conf.urls import *
from tastypie.api import Api

from apps.main.api import AuctionResource
from apps.main.api import MemberAuctionsResource
from apps.main.api import BidPackageResource
from apps.main.api import CategoryResource
from apps.main.api import ConverTokensResource
from apps.main.api import ItemResource
from apps.main.api import MemberByFBTokenResource
from apps.main.api import MemberResource
from apps.main.api import NotificationResource
from apps.main.api import MessageResource
from apps.main.api import AddBidResource
from apps.main.api import ClaimBidResource
from apps.main.api import RemBidResource


from apps.main.api import RegisterInvitationResource
from apps.main.api import ServerClockResource

from apps.main.api import PaypalPaymentInfoResource
from apps.main.api import IOPaymentInfoResource
from apps.main.api import AppleIbidPackageIdsResource

v1_api = Api(api_name='v1')

v1_api.register(RegisterInvitationResource())
v1_api.register(ServerClockResource())
v1_api.register(NotificationResource())
v1_api.register(MemberResource())
v1_api.register(ConverTokensResource())
v1_api.register(MemberByFBTokenResource())
v1_api.register(CategoryResource())
v1_api.register(ItemResource())
v1_api.register(AuctionResource())
v1_api.register(MemberAuctionsResource())
v1_api.register(BidPackageResource())
v1_api.register(AddBidResource())
v1_api.register(RemBidResource())
v1_api.register(ClaimBidResource())
v1_api.register(MessageResource())
v1_api.register(IOPaymentInfoResource())
v1_api.register(AppleIbidPackageIdsResource())
v1_api.register(PaypalPaymentInfoResource())


urlpatterns = patterns('',

#############################
    url(r"^%s$" % (NotificationResource()._meta.resource_name), NotificationResource.get, name="notification_dispatch_list"),
    url(r"^%s/(?P<pk>\d+)/$" % (NotificationResource()._meta.resource_name), NotificationResource.put, name="notification_dispatch_detail"),
    
    url(r"^%s$" % (MemberResource()._meta.resource_name), MemberResource.get, name="member_dispatch_list"),
    url(r"^%s/(?P<%s>\d+)$" % (MemberResource()._meta.resource_name, MemberResource()._meta.detail_uri_name), MemberResource.retrieve, name="member_dispatch_detail"),
    
    url(r"^member/%s/(?P<member_id>\d+)$" % (ConverTokensResource()._meta.resource_name), ConverTokensResource.get, name="convertTokens"),
    
    url(r"^member/%s/(?P<%s>.*?)$" % (MemberByFBTokenResource()._meta.resource_name, MemberByFBTokenResource()._meta.detail_uri_name), MemberByFBTokenResource.get, name="api_dispatch_detail"),
    
    url(r"^%s$" % (CategoryResource()._meta.resource_name), CategoryResource.get, name="category_dispatch_list"),
    url(r"^%s/(?P<%s>\d+)$" % (CategoryResource()._meta.resource_name, CategoryResource()._meta.detail_uri_name), CategoryResource.retrieve, name="category_dispatch_detail"),
    
    url(r"^%s$" % (ItemResource()._meta.resource_name), ItemResource.get, name="items_dispatch_list"),
    url(r"^%s/(?P<%s>\d+)$" % (ItemResource()._meta.resource_name, ItemResource()._meta.detail_uri_name), ItemResource.retrieve, name="items_dispatch_detail"),
    
    url(r"^%s$" % (AuctionResource()._meta.resource_name), AuctionResource.get, name="auctions_dispatch_list"),
    url(r"^%s/(?P<%s>\d+)$" % (AuctionResource()._meta.resource_name, AuctionResource()._meta.detail_uri_name), AuctionResource.retrieve, name="auctions_dispatch_detail"),
    
    url(r"^member/%s/$" % (MemberAuctionsResource()._meta.resource_name), MemberAuctionsResource.get, name="my_auctions_dispatch_list"),
    
    url(r"^%s$" % (BidPackageResource()._meta.resource_name), BidPackageResource.get, name="bid_package_dispatch_list"),
    url(r"^%s/(?P<%s>\d+)$" % (BidPackageResource()._meta.resource_name, BidPackageResource()._meta.detail_uri_name), BidPackageResource.retrieve, name="bid_package_dispatch_detail"),
    
    url(r"^auction/(?P<auction_id>\d+)/%s/$" %(AddBidResource()._meta.resource_name), AddBidResource.post, name="add_bids_dispatch_detail"),
    url(r"^auction/(?P<auction_id>\d+)/%s/$" %(RemBidResource()._meta.resource_name), RemBidResource.post, name="rem_bids_dispatch_detail"),
    url(r"^auction/(?P<auction_id>\d+)/%s/$" %(ClaimBidResource()._meta.resource_name), ClaimBidResource.post, name="rem_bids_dispatch_detail"),
    
    url(r"^auction/(?P<auction_id>\d+)/%s/$" %(MessageResource()._meta.resource_name), MessageResource.post, name="messages_dispatch_detail"),
    
    url(r"^%s$" % (IOPaymentInfoResource()._meta.resource_name), IOPaymentInfoResource.post, name="payment_io_dispatch_list"),
    
    url(r"^%s$" % (AppleIbidPackageIdsResource()._meta.resource_name), AppleIbidPackageIdsResource.get, name="apple_ibid_bid_package_dispatch_list"),
    
    url(r"^%s$" % (RegisterInvitationResource()._meta.resource_name), RegisterInvitationResource.post, name="register_invitation_resource_dispatch_list"),
#############################
    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^api/', include(v1_api.urls)),


)

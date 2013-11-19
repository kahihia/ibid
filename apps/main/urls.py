# -*- coding: utf-8 -*-
from django.conf.urls import *
from tastypie.api import Api

from apps.main.api import CategoryResource,AuctionsWonByUserResource,NotificationResource,AuctionResource,MemberResource,MemberByFBTokenResource,ConverTokensResource,BidPackageResource,SendMessageResource,ItemResource,joinAuctionResource,addBidResource,remBidResource,claimBidResource
#,AuctionAvailableResource,AuctionFinishedResource,AuctionByCategoryResource

v1_api = Api(api_name='v1')
v1_api.register(NotificationResource())
v1_api.register(AuctionResource())
v1_api.register(MemberResource())
v1_api.register(MemberByFBTokenResource())
v1_api.register(ConverTokensResource())
v1_api.register(BidPackageResource())
v1_api.register(CategoryResource())
v1_api.register(SendMessageResource())
v1_api.register(ItemResource())
v1_api.register(addBidResource())
v1_api.register(remBidResource())
v1_api.register(claimBidResource())
v1_api.register(joinAuctionResource())
#v1_api.register(AuctionAvailableResource())
#v1_api.register(AuctionFinishedResource())
#v1_api.register(AuctionByCategoryResource())
v1_api.register(AuctionsWonByUserResource())

urlpatterns = patterns('',
    (r'^api/doc/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    (r'^api/', include(v1_api.urls)),
)


# -*- coding: utf-8 -*-
from django.conf.urls import *
from tastypie.api import Api

from apps.main.api import NotificationResource, UserByFBTokenResource,AuctionResource,MemberResource,BidPackageResource


v1_api = Api(api_name='v1')
v1_api.register(NotificationResource())
v1_api.register(UserByFBTokenResource())
v1_api.register(AuctionResource())
v1_api.register(MemberResource())
v1_api.register(BidPackageResource())


urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)


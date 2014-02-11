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
from apps.main.api import IOPaymentInfoResource
from apps.main.api import AppleIbidPackageIdsResource

v1_api = Api(api_name='v1')
v1_api.register(AuctionResource())
v1_api.register(MemberAuctionsResource())
v1_api.register(BidPackageResource())
v1_api.register(CategoryResource())
v1_api.register(ConverTokensResource())
v1_api.register(ItemResource())
v1_api.register(MemberByFBTokenResource())
v1_api.register(MemberResource())
v1_api.register(NotificationResource())
v1_api.register(MessageResource())
v1_api.register(AddBidResource())
v1_api.register(ClaimBidResource())
v1_api.register(RemBidResource())
v1_api.register(IOPaymentInfoResource())
v1_api.register(AppleIbidPackageIdsResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)

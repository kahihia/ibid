# -*- coding: utf-8 -*-
from django.conf.urls import *
from tastypie.api import Api

from apps.main.api import NotificationResource, LoginByFBTokenResource


v1_api = Api(api_name='v1')
v1_api.register(NotificationResource())
v1_api.register(LoginByFBTokenResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)


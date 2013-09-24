# -*- coding: utf-8 -*-
from django.conf.urls import *
from tastypie.api import Api

from apps.main.api import NotificationResource


v1_api = Api(api_name='v1')
v1_api.register(NotificationResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)


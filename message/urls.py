# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('message.views',
                        url(r'^action/$', 'message_listener', name='event_listener'),
)



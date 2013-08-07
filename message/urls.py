# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('message.views',
                        url(r'^action/(?P<method>\w+)/$', 'message_listener', name='event_listener'),
                        url(r'^staatic/$', 'static', name='static'),

)



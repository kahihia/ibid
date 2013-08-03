# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('event.views',
                        url(r'^event/(?P<method>\w+)/$', 'event_listener', name='event_listener'),
)



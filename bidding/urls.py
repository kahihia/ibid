# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from bidding.views.home import CurrencyHistory


urlpatterns = patterns('bidding.views.home',
                       url(r'^$', 'canvashome', name='bidding_anonym_home'),
                       url(r'^canvashome/$', 'canvashome', name='canvashome'),
                       url(r'^canvasapp/$', 'canvasapp', name='canvasapp'),
                       url(r'^home/$', 'canvashome', name='bidding_home'),
                       url(r'^fb/$', 'canvashome', name='fb_auth'),
                       url(r'^examples/404/$', 'example_404', name='example_404'),
                       url(r'^examples/500/$', 'example_500', name='example_500'),
                       url(r'^examples/winner_email/$', 'winner_email_example'),
                       url(r'^history/$', CurrencyHistory.as_view(), name='history'),
                       url(r'^promo/$', 'promo', name='promo'),
                       url(r'^standalone/$', 'standalone', name='standalone'),
                       url(r'^winners/(?P<page>\d+)/$', 'winners', name='bidding_winners'),
                       url(r'^won_list/$', 'auction_won_list', name='bidding_auction_won_list'),
)

urlpatterns += patterns('bidding.views.facebook',
                        url(r'^bid_package/(?P<package_id>\d+)$','bid_package_info', name='bid_package'),
                        url(r'^fb_callback/$', 'credits_callback', name='fb_callback'),
                        url(r'^fb_deauthorized/$', 'deauthorized_callback', name='fb_deauthorized'),
                        url(r'^fb_check_like/$', 'fb_check_like', name='fb_check_like'),
                        url(r'^fb_like/$', 'fb_like', name='fb_like'),
                        url(r'^fb_place_order/$', 'place_order', name='place_order'),
                        url(r'^fb_item/(?P<item_id>\d+)$', 'fb_item_info', name='fb_item_info'),
                        url(r'^fb_redirect/$', 'fb_redirect', name='fb_redirect'),
                        url(r'^fb_test/$', 'fb_test_user', name='fb_test'),
                        url(r'^invite/$', 'store_invitation', name='fb_invite'),
)

urlpatterns += patterns('bidding.views.api',
                        url(r'^api/(?P<method>\w+)/$', 'api', name='api'),
)

urlpatterns += patterns('bidding.views.paypal_views',
                        url(r'^buy_item/(?P<id>[-\w]+)/$', 'buy_item', name='bidding_buy_item'), #REMOVED:{'SSL':True}
)

urlpatterns += patterns('',
                        url(r'^leave/$', TemplateView.as_view(template_name="404.html"), name='bidding_leave_auction'),
)



from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from bidding.views.home import CurrencyHistory


urlpatterns = patterns('bidding.views.home',
                       url(r'^winners/(?P<page>\d+)/$', 'winners', name='bidding_winners'),
                       url(r'^won_list/$', 'auction_won_list', name='bidding_auction_won_list'),
                       url(r'^$', 'web_home', name='bidding_anonym_home'),
                       url(r'^home/$', 'canvashome', name='bidding_home'),
                       url(r'^canvashome/$', 'canvashome', name='canvashome'),
                       #url(r'^canvaslogin/$', 'canvaslogin', name='canvaslogin'),
                       url(r'^history/$', CurrencyHistory.as_view(), name='history'),
                       url(r'^faq2/$', 'faq', name='faq'),
                       url(r'^examples/winner_email/$', 'winner_email_example'),
                       url(r'^examples/404/$', 'example_404', name='example_404'),
                       url(r'^examples/500/$', 'example_500', name='example_500'),
                       url(r'^promo/$', 'promo', name='promo'),
                       #url(r'^run_fixture/$', 'run_fixture', name='bidding_run_fixture'),
                       url(r'^standalone/$', 'standalone', name='standalone'),
)

urlpatterns += patterns('bidding.views.facebook',
                        
                        url(r'^fb_redirect/$', 'fb_redirect', name='fb_redirect'),
                        url(r'^fb/$', 'fb_auth', name='fb_auth'),
                        url(r'^fb/login/$', 'fb_login', name='fb_login'),
                        url(r'^fb_test/$', 'fb_test_user', name='fb_test'),
                        url(r'^invite/$', 'store_invitation', name='fb_invite'),
                        url(r'^fb_callback/$', 'credits_callback', name='fb_callback'),
                        url(r'^fb_deauthorized/$', 'deauthorized_callback', name='fb_deauthorized'),
                        url(r'^fb_place_order/$', 'place_order', name='place_order'),
                        url(r'^fb_item/(?P<item_id>\d+)$', 'fb_item_info', name='fb_item_info'),
)

urlpatterns += patterns('bidding.views.api',
                        url(r'^api/(?P<method>\w+)/$', 'api', name='api'),
)

urlpatterns += patterns('bidding.views.paypal_views',
                        url(r'^buy_item/(?P<id>[-\w]+)/$', 'buy_item', name='bidding_buy_item'), #REMOVED:{'SSL':True}
)

urlpatterns += patterns('',
                        url(r'^leave/$', TemplateView.as_view(template_name="404.html"), name='bidding_leave_auction'),
                        url(r'^fb_test_item/$', TemplateView.as_view(template_name="fb_test_item.html"), name='fb_test_item'),
)

#this is important, if not here this more_signals wont be included anywhere and stuff there wont work!
import more_signals

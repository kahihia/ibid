from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from bidding.views.home import CurrencyHistory


urlpatterns = patterns('bidding.views.home',
            url(r'^$', 'web_home', name='bidding_anonym_home'),
            url(r'^home/$', 'mainpage', name='bidding_home'),
            url(r'^canvashome/$', 'canvashome', name='canvashome'),
            #url(r'^canvaslogin/$', 'canvaslogin', name='canvaslogin'),
            url(r'^history/$', CurrencyHistory.as_view(), name='history'),
            url(r'^promoted_redirected/(?P<auction_id>\d+)/$', 'promoted', name='promoted'), #show the auction
            url(r'^faq2/$', 'faq', name='faq'),
)

urlpatterns += patterns('',
    
    url(r'^winners/(?P<page>\d+)/$', 'bidding.views.auctions.winners', name='bidding_winners'),
    url(r'^won_list/$', 'bidding.views.auctions.auction_won_list', name='bidding_auction_won_list'),
    url(r'^auction/(?P<slug>[\w-]+)/(?P<id>\d+)/$', 'bidding.views.auctions.auction_detail', name='bidding_auction_detail'),
    
    url(r'^update_detail/(?P<auction_id>\d+)/$', 'bidding.views.auctions.auction_detail_update', name='bidding_detail_update'),
    
    url(r'^bid/$', 'bidding.views.auctions.bid', name='bidding_bid'),
    url(r'^precap_bid/$', 'bidding.views.auctions.precap_bid', name='bidding_precap_bid'),
    url(r'^first_precap/$', 'bidding.views.auctions.first_precap', name='bidding_precap_first'),
    url(r'^leave/$', 'bidding.views.auctions.leave_auction', name='bidding_leave_auction'),
    url(r'^sync_timers/$', 'bidding.views.auctions.sync_timers', name='bidding_sync_timers'),
    url(r'^auct_timers/(?P<auction_id>\d+)/$', 'bidding.views.auctions.sync_auction_timer', name='bidding_auct_timers'),

    url(r'^item_price/$', 'bidding.views.auctions.item_price', name='bidding_item_price'),
    url(r'^run_fixture/$', 'bidding.views.auctions.run_fixture', name='bidding_run_fixture'),
    url(r'^item_info/$', 'bidding.views.auctions.item_info', name='bidding_item_info'),
    url(r'^participants/$', 'bidding.views.auctions.update_participants_page', name='bidding_participants'),
    url(r'^user_bids/$', 'bidding.views.auctions.user_bids', name='bidding_user_bids'),
    url(r'^convert_tokens/$', 'bidding.views.auctions.convert_tokens', name='convert_tokens'),
)

urlpatterns += patterns('bidding.views.browse',
    url(r'^browse/$', 'browse_auctions', name='bidding_browse'),
    url(r'^update_browse/$', 'update_browse_page', name='bidding_update_browse'),
    url(r'^search/$', 'search_autocomplete', name='bidding_autocomplete'),
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
)

urlpatterns += patterns('bidding.views.auctions',
    url(r'^create_promoted/$', 'create_promoted', name='create_promoted'), 
    url(r'^promoted/(?P<auction_id>\d+)/$', 'redirect_promoted', name='redirect_promoted'), #savees the cookie and send the user into fb
)

urlpatterns += patterns('bidding.views.wise',
    url(r'^info/init/$', 'init', name='info_init'), 
    url(r'^info/load_auction/$', 'load_auction', name='load_auction'), 
    url(r'^reloadTokens/$', 'reloadTokens', name='reloadTokens'), 
    url(r'^wise/inviteRequest/$', 'inviteRequest', name='inviteRequest'), 
)

urlpatterns += patterns('bidding.views.api',
    url(r'^api/(?P<method>\w+)/$', 'api', name='api'),
)

urlpatterns += patterns('bidding.views.apitest',
    url(r'^apitest/(?P<method>\w+)/$', 'apitest', name='apitest'),
)

urlpatterns += patterns('bidding.views.bidapi',
    url(r'^bid_service/api/(?P<method>\w+)/$', 'api', name='api'),
)


urlpatterns += patterns('bidding.views.paypal_views',
    url(r'^buy_item/(?P<id>[-\w]+)/$', 'buy_item', name='bidding_buy_item'), #REMOVED:{'SSL':True}
)

urlpatterns += patterns('',
    url(r'^leave/$', TemplateView.as_view(template_name = "404.html"), name='bidding_leave_auction'),
)

import more_signals
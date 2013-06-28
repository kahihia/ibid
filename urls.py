from django.conf.urls import patterns, url, include
from django.views.generic.base import RedirectView
from bidding.sitemaps import AuctionSitemap
from django.contrib.sitemaps import FlatPageSitemap
from django.conf import settings
import os.path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

sitemaps={'auctions': AuctionSitemap, 'flatpages':FlatPageSitemap}

urlpatterns = patterns('',
    # Example:
    
    (r'', include('bidding.urls')),
    (r'^chat/', include('chat.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')),


    url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps':sitemaps}, name="sitemap"),
)

urlpatterns += patterns('',
	url(r'^winners/$', RedirectView.as_view(url='/winners/1/'), name='bidding_winners_redirect'),
    (r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^static/(?P<path>.*)$', 'serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'static')}),
        (r'^media/(?P<path>.*)$', 'serve', {'document_root': os.path.join(settings.PROJECT_PATH, 'media')}),

    )

import os.path

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic.base import RedirectView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'api/doc/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    (r'', include('apps.main.urls')),
    (r'', include('bidding.urls')),
    (r'', include('message.urls')),
    (r'^chat/', include('chat.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'api/doc/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    
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

if 'sandbox' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^sandbox/', include('sandbox.urls')))

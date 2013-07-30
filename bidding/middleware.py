__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

SSL = 'SSL'

class SSLRedirect:
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if not secure == self._is_secure(request):
            return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
	    return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,request.get_host(),request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponsePermanentRedirect(newurl)

class P3PHeaderMiddleware(object):
    def process_response(self, request, response):
        #response['P3P'] = getattr(settings, 'P3P_COMPACT_SAFARI', None)
        response['P3P'] = 'policyref="/w3c/p3p.xml", CP="NOI DSP COR NID CUR ADM DEV OUR BUS"'
        response['P3P'] = 'policyref="/w3c/p3p.xml", CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR", Access-Control-Allow-Origin: *'
        response['Access-Control-Allow-Origin'] = '*'
        response['Set-Cookie'] = "test_cookie=1"


        #response['P3P'] = getattr(settings, 'P3P_COMPACT_IE', None) + ', ' + getattr(settings, 'P3P_COMPACT_SAFARI', None)
        return response
        



# -*- coding: utf-8 -*-

from settings import *


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q0zs)p0r6h2u1^b5ak55z)nuu^mvi*rd4jx6$!=++_xqv6s(qq'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

#error reports
SEND_BROKEN_LINK_EMAILS = False

# Logging
LOGGING['handlers']['file']['filename]' = '/tmp/ibiddjango.log'
LOGGING['handlers']['sql']['filename'] = '/tmp/sql.log'
LOGGING['handlers']['commands']['filename'] = '/tmp/commands.log'

# Urls
WEB_APP = "http://localhost:8000/"
NOT_AUTHORIZED_PAGE = WEB_APP
APP_FIRST_REDIRECT = WEB_APP + "fb_redirect/"
FB_APP = "http://apps.facebook.com/interactivebids/"
FBAPP = WEB_APP + "fb/"
FBAPP_HOME = FB_APP + "home/"
CANVAS_HOME = FB_APP + "canvashome/"
#see how to better handle this
IMAGES_SITE = '' #'http://apps.facebook.com/interactivebids'
SITE_NAME = 'http://localhost:8000'
BID_SERVICE = 'http://localhost:8000/bid_service/api/'
COUNTDOWN_SERVICE = 'http://localhost:8000/countdown/api/'

# Facebook settings (more on settings_secret)
AUTH_REDIRECT_URI = '{protocol}://apps.facebook.com/interactivebids/fb/login/'

# App Settings
ERROR_REPORT_TITLE = "IBG ERROR REPORT LOCAL"

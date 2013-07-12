# -*- coding: utf-8 -*-

from settings import *


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q0zs)p0r6h2u1^b5ak55z)nuu^mvi*rd4jx6$!=++_xqv6s(qq'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = 'test@nuske.com.ar'
SERVER_EMAIL = 'test@nuske.com.ar'

# Logging
LOGGING['handlers']['file']['filename]' = '/var/apps/apps.facebook.ibidgames.com/logs/ibiddjango.log'
LOGGING['handlers']['sql']['filename'] = '/var/apps/apps.facebook.ibidgames.com/logs/sql.log'
LOGGING['handlers']['commands']['filename'] = '/var/apps/apps.facebook.ibidgames.com/logs/commands.log'

# Urls
WEB_APP = "http://dev.facebook.ibidgames.com/"
NOT_AUTHORIZED_PAGE = WEB_APP
APP_FIRST_REDIRECT = WEB_APP + "fb_redirect/"
FB_APP = "http://apps.facebook.com/ibidgames-dev/"
FBAPP = WEB_APP + "fb/"
FBAPP_HOME = FB_APP + "home/"
CANVAS_HOME = FB_APP + "canvashome/"
#see how to better handle this
IMAGES_SITE = 'http://dev.facebook.ibidgames.com'
SITE_NAME = 'http://dev.facebook.ibidgames.com'
BID_SERVICE = 'http://dev.facebook.ibidgames.com/bid_service/api/'
COUNTDOWN_SERVICE = 'http://dev.facebook.ibidgames.com/countdown/api/'

# Facebook settings (more on settings_secret)
AUTH_REDIRECT_URI = '{protocol}://apps.facebook.com/ibidgames-dev/fb/login/'

# App Settings
ERROR_REPORT_TITLE = "IBG ERROR REPORT TOMATO-DEV"

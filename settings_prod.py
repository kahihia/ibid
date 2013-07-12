# -*- coding: utf-8 -*-

from settings import *


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q0zs)p0r6h2u1^b5ak55z)nuu^mvi*rd4jx6$!=++_xqv6s(aa'

# Media files
MEDIA_ROOT = '/var/www/media.ibidgames.com/'

# Logging
LOGGING['handlers']['file']['filename]' = '/var/www/facebook.ibidgames.com/logs/ibiddjango.log'
LOGGING['handlers']['sql']['filename'] = '/var/www/facebook.ibidgames.com/logs/sql.log'
LOGGING['handlers']['commands']['filename'] = '/var/www/facebook.ibidgames.com/logs/commands.log'

# Urls
WEB_APP = "https://apps.facebook.ibidgames.com/"
NOT_AUTHORIZED_PAGE = WEB_APP
APP_FIRST_REDIRECT = WEB_APP + "fb_redirect/"
FB_APP = "https://apps.facebook.com/ibidgames/"
FBAPP = WEB_APP + "fb/"
FBAPP_HOME = FB_APP + "home/"
CANVAS_HOME = FB_APP + "canvashome/"
#see how to better handle this
IMAGES_SITE = 'https://apps.facebook.ibidgames.com'
SITE_NAME = 'https://apps.facebook.ibidgames.com/'
BID_SERVICE = 'http://apps.facebook.ibidgames.com/bid_service/api/'
COUNTDOWN_SERVICE = 'http://apps.facebook.ibidgames.com/countdown/api/'

# Facebook settings (more on settings_secret)
AUTH_REDIRECT_URI = '{protocol}://apps.facebook.com/ibidgames/fb/login/'

# App Settings
ERROR_REPORT_TITLE = "IBG ERROR REPORT PROD COCONUT-MASTER"

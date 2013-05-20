# Django settings for marpasoftsite project.
import os.path

try:
    from settings_local import DEBUG
except ImportError:
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ['127.0.0.1']

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_FROM_EMAIL = 'info@ibidchat.com'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'info@ibidchat.com'
EMAIL_HOST_PASSWORD = 'ibidchat11'
EMAIL_USE_TLS = True


ADMINS = (
    ('dnuske', 'dnuske@isolutionspro.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'django_facebook.auth_backends.FacebookBackend',)
REGISTRATION_BACKEND = 'ibiddjango.authbackends.YambidRegistration'

AUTH_PROFILE_MODULE = 'bidding.member'
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: '/bids/user/%s/' % o.username
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media') 

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q0zs)p0r6h2u1^b5ak55z)nuu^mvi*rd4jx6$!=++_xqv6s(qq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'routines.middleware.DualSessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'bidding.middleware.SSLRedirect',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "routines.context_processors.current_site",
    "routines.context_processors.static_media",
    "bidding.context_processors.orbited_address",
    "bidding.context_processors.connections",
    'django_facebook.context_processors.facebook',
    )


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'monkey_patch',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'django.contrib.messages',

    'bidding',
    'chat',

    'paypal.standard.ipn',
    'routines',
    'sorl.thumbnail',
    'south',
    'django_extensions',
    
    'kombu.transport.django', 
    'djcelery',
    
    #Needed by django facebook
    'registration',
    'django_facebook',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file':{
                'class' : 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': '/var/www/ibiddjango/../logs/ibiddjango.log',
                'maxBytes': 10240,
                'backupCount': 3,
        },
                 
        'commands':{
                'class' : 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': '/var/www/ibiddjango/../logs/commands.log',
                'maxBytes': 10240,
                'backupCount': 3,
        },
    
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'INFO',
        },        
        'scheduling': {
            'handlers':['commands'],
            'propagate': True,
            'level':'DEBUG',
        },
        
    }
}


LOGIN_REDIRECT_URL = "/"

#ORBITED_DOMAIN = 'www.ibiddjango.net'
ORBITED_DOMAIN = ''
ORBITED_PORT = 8500
ORBITED_SECURE_PORT = 8043
ORBITED_STATIC_URL = '/static/'

MESSAGING_PROCESS = "orbited"

RECAPTCHA_PUB_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""


if not DEBUG:
    SITE_NAME = 'http://bid711.com'
    PAYPAL_RECEIVER_EMAIL = 'info@isolutionspro.com'
else:
    SITE_NAME = 'http://bid711.com'
    PAYPAL_RECEIVER_EMAIL = 'dnuske@gmail.com'

#see how to better handle this
IMAGES_SITE = 'http://www.bid711.com'

    
EMAIL_CONFIRMATION_DAYS = 5
PERSISTENT_SESSION_KEY='sessionpersistent'

ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

try:
    from settings_local import *
    from facebook_settings import *
except ImportError:
    pass

#CELERY
import djcelery
djcelery.setup_loader()

#celery
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"


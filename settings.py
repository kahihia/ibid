# Django settings for marpasoftsite project.
import os.path

try:
    from settings_local import DEBUG
except ImportError:
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

#INTERNAL_IPS = ['127.0.0.1']

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_FROM_EMAIL = 'info@ibidgames.com'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
#EMAIL_HOST_USER = 'daniel@nuske.com.ar'
#EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = 'info@ibidgames.com'
EMAIL_HOST_PASSWORD = 'Supernuske13'
EMAIL_USE_TLS = True


ADMINS = (
    ('Daniel', 'dnuske@gmail.com'),
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
FACEBOOK_REGISTRATION_BACKEND = 'ibiddjango.authbackends.YambidRegistration'

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
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
    "bidding.context_processors.settings_context",
    'django_facebook.context_processors.facebook',
    "bidding.context_processors.packages_context",
    )


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
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
    
    #'kombu.transport.django',

    #Needed by django facebook
    'registration',
    'django_facebook',
    #'debug_toolbar',
    #'iframetoolbox'
)

INTERNAL_IPS = ('67.23.8.95',)

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
                'filename': '/var/www/logs/ibiddjango.log',
                'maxBytes': 1024000,
                'backupCount': 3,
        },
        'sql':{
            'class' : 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/var/www/logs/yambid_sql.log',
            'maxBytes': 102400,
            'backupCount': 3,
            },
        'commands':{
                'class' : 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': '/var/www/logs/commands.log',
                'maxBytes': 10240,
                'backupCount': 3,
        },
    
    },
    'loggers': {
        'django': {
            'handlers':['file', 'console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.db.backends': {
            'handlers':['sql', 'console'],
            'propagate': False,
            'level':'WARNING',
        },
        'scheduling': {
            'handlers':['commands', 'console'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}


LOGIN_REDIRECT_URL = "/"

#ORBITED_DOMAIN = 'www.ibiddjango.net'
#ORBITED_DOMAIN = ''
#ORBITED_PORT = 8500
#ORBITED_SECURE_PORT = 8043
#ORBITED_STATIC_URL = '/static/'

#STOMP_PORT = 61613

# MESSAGING_PROCESS = "orbited"

RECAPTCHA_PUB_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""


if not DEBUG:
    SITE_NAME = 'http://apps.facebook.com/interactivebids'
    PAYPAL_RECEIVER_EMAIL = 'payment@ibidgames.com'
else:
    SITE_NAME = 'http://apps.facebook.com/interactivebids'
    PAYPAL_RECEIVER_EMAIL = 'payment@ibidgames.com'

#see how to better handle this
IMAGES_SITE = 'http://localhost:8000' #'http://apps.facebook.com/interactivebids'

    
EMAIL_CONFIRMATION_DAYS = 5
PERSISTENT_SESSION_KEY='sessionpersistent'

ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

try:
    from settings_local import *
    from facebook_settings import *
except ImportError:
    print "here it goes <-----------"
    pass

#CELERY
#import djcelery
#djcelery.setup_loader()

#celery
#BROKER_HOST = "localhost"
#BROKER_PORT = 5672
#BROKER_USER = "guest"
#BROKER_PASSWORD = "guest"
#BROKER_VHOST = "/"

TOKENS_TO_BIDS_RATE = 0.001

PAGINATED_BY = 20

NOT_AUTHORIZED_PAGE = "http://apps.facebook.com/interactivebids"
FBAPP_HOME = "http://apps.facebook.com/interactivebids/home"
CANVAS_HOME = "http://apps.facebook.com/interactivebids/canvashome/"

#P3P_COMPACT = 'policyref="http://www.example.com/p3p.xml", CP="NON DSP COR CURa TIA"'
P3P_COMPACT_IE = 'policyref="http://www.example.com/p3p.xml", CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT", Access-Control-Allow-Origin: *'
P3P_COMPACT_SAFARI = 'P3P: CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR", Access-Control-Allow-Origin: *'
MIDDLEWARE_CLASSES += ('bidding.middleware.P3PHeaderMiddleware',)
#MIDDLEWARE_CLASSES += 'iframetoolbox.middleware.IFrameFixMiddleware'


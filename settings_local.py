DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':   'ibiddjango',                      # Or path to database file if using sqlite3.
        'USER':   'ibiddjango',                      # Not used with sqlite3.
        'PASSWORD': 'ibiddjango',                  # Not used with sqlite3.
        'HOST':   'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT':   '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {'autocommit': True},
    }
}

ORBITED_DOMAIN = 'www.ibidgames.com'
ORBITED_PORT = 8500
ORBITED_SECURE_PORT = 8043
ORBITED_STATIC_URL = '/static/'

MESSAGING_PROCESS = "orbited"

RECAPTCHA_PUB_KEY = "6LdGTwYAAAAAAKE_4uTdZS0CFQoOUVYuDc0Dhvca"
RECAPTCHA_PRIVATE_KEY = "6LdGTwYAAAAAAE_yfsWHZbLJhKjta1EcKPXOfhjL"

FACEBOOK_FORCE_PROFILE_UPDATE_ON_LOGIN = True

ERROR_REPORT_TITLE = "IBG ERROR REPORT"

#dev

PUBNUB_PUB = "pub-c-4b483b5a-de1a-40af-b81f-171d2ee61712"
PUBNUB_SUB = "sub-c-6167b316-c410-11e2-8a13-02ee2ddab7fe"
PUBNUB_SECRET = ''

#heroku
#PUBNUB_PUB = "pub-c-d1a46dfc-ba36-4a4b-b8e8-e5fd8852a710"
#PUBNUB_SUB = "sub-c-ffeca876-b2a8-11e2-92b8-02ee2ddab7fe"


#prod
#PUBNUB_PUB = "pub-c-ac47e3eb-4c28-4688-a6d2-6656c50236a9"
#PUBNUB_SUB = "sub-c-448cc678-b2a9-11e2-9393-02ee2ddab7fe"


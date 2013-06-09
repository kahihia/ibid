DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ibidgamesdjango',                      # Or path to database file if using sqlite3.
        'USER': 'ibid',                      # Not used with sqlite3.
        'PASSWORD': 'ibidcalabazaesencial',                  # Not used with sqlite3.
        'HOST': '10.178.67.90',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {'autocommit': True},
    }
}

ORBITED_DOMAIN = 'www.ibidville.com'
ORBITED_PORT = 8500
ORBITED_SECURE_PORT = 8043
ORBITED_STATIC_URL = '/static/'

MESSAGING_PROCESS = "orbited"

RECAPTCHA_PUB_KEY = "6LdGTwYAAAAAAKE_4uTdZS0CFQoOUVYuDc0Dhvca"
RECAPTCHA_PRIVATE_KEY = "6LdGTwYAAAAAAE_yfsWHZbLJhKjta1EcKPXOfhjL"

FACEBOOK_FORCE_PROFILE_UPDATE_ON_LOGIN = True

ERROR_REPORT_TITLE = "IBG ERROR REPORT DEV"

#dev
#PUBNUB_PUB = "pub-c-7a4bd941-9b92-47b3-931f-491fdccb3be1"
#PUBNUB_SUB = "sub-c-ba10f43c-bbd2-11e2-a0b6-02ee2ddab7fe"

#prod
PUBNUB_PUB = "pub-c-7a4bd941-9b92-47b3-931f-491fdccb3be1"
PUBNUB_SUB = "sub-c-ba10f43c-bbd2-11e2-a0b6-02ee2ddab7fe"
PUBNUB_SECRET = ''

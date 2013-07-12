Interactive Bid Games Inc. http://ibidgames.com

System requirements:

    * livevent-dev
    * supervisor==3.0b1
    * libjpeg-dev
    * libpng-dev
    * PIL==1.1.7
    * libmysqlclient-dev
    * MySQL-python

Written using Django 1.5.1

see requirements.txt for requirements list


Settings
========

Default settings are provided in the file settings_default.py, this file should
be extended in your settings.py file (see settings.py-example to see the main
things you should configure).

To extend this file, create a settings.py file like this:

```python
from settings_default import *

FACEBOOK_API_KEY = 'asdfasdf'
FACEBOOK_APP_ID = 'sdfasdfasdf'
FACEBOOK_APP_SECRET = ''
```

The settings.py file is excluded from the repo to avoid conflicts with
production settings. Please don't commit it.

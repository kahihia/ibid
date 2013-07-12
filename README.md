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

The main settings file imports the settings_secret.py file, which is not
commited and is different for each environment. It storesdb credentials, api
keys, etc. An example empy secrets file is provided in
settings_secret.py-example, copy and edit it.

Each envirnonment has it's own settings file, which inherits from the main
settins.py file.

To start the application, set the DJANGO_SETTINGS_MODULE variable and then run
it as usual:

  $ export DJANGO_SETTINGS_MODULE='settings_local'
  $ ./manage.py runserver

Provided environmen files are:
 * settings_prod.py - Production environment (coconut-* servers)
 * settings_dev.py - Develop/testing environment (tomato-dev)
 * settings_local.py - Local develop environment.

You can commit on any of these files, but if you need to set up some private
stuff that should go in settings_secret.py, we have to add it manually in each
environment so ask how to deal with this.


Custom settings files
---------------------

You can extend any settings file customizing your stuff by extending the
settings_local.py file (or any other settings file) in the settings_custom.py
file and changing what's needed. This file is also exluded from the repos so
it's safe to change it.

You can use it to test apps, cofigs, change your dbs to something else, etc.

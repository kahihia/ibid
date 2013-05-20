bind = "127.0.0.1:8888"
workers = 3
secure_scheme_headers={'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-SSL': 'on'}
accesslog = "/var/www/ibiddjango/gunicorn.access.log"
errorlog = "/var/www/ibiddjango/gunicorn.access.log"

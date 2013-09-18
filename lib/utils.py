# -*- coding: utf8 -*-

import urlparse

from django.templatetags.static import static
from django.conf import settings


def get_static_url(path):
    parts1 = urlparse.urlparse(settings.IMAGES_SITE)
    parts2 = urlparse.urlparse(static(path))
    parts = parts1[:2] + parts2[2:]
    url = urlparse.urlunparse(parts)
    return url

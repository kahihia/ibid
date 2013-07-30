from django.conf import settings

from bidding.models import BidPackage


def settings_context(request):
    if '//' in settings.SITE_NAME:
        site_name = settings.SITE_NAME.split('//')[1]
    else:
        site_name = settings.SITE_NAME
    return {'SITE_NAME' : site_name}


def packages_context(request):
    return {'packages': BidPackage.objects.all().order_by('price')}

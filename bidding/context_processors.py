from django.conf import settings
from bidding.models import BidPackage
from sslutils import is_secure, get_protocol

def settings_context(request):
    return {'SITE_NAME' : settings.SITE_NAME.strip('http://')}

def packages_context(request):
    return {'packages': BidPackage.objects.all().order_by('price')}
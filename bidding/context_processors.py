from django.conf import settings
from bidding.models import BidPackage
from sslutils import is_secure, get_protocol

def orbited_address(request):
    port = settings.ORBITED_SECURE_PORT if is_secure(request) else settings.ORBITED_PORT
    protocol = get_protocol(request)
    
    return {'ORBITED_DOMAIN':settings.ORBITED_DOMAIN,
            'ORBITED_PORT':port,
            'ORBITED_STATIC_URL':settings.ORBITED_STATIC_URL,
            'ORBITED_PROTOCOL' : protocol}

def settings_context(request):
    return {'SITE_NAME' : settings.SITE_NAME.strip('http://')}

def packages_context(request):
    return {'packages': BidPackage.objects.all().order_by('price')}
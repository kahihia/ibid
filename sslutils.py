

def is_secure(request):
    return ('HTTP_X_FORWARDED_PROTOCOL' in request.META and 
                request.META['HTTP_X_FORWARDED_PROTOCOL'] == 'https')

def get_protocol(request):
    return 'https' if is_secure(request) else 'http'
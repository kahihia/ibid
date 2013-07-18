from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django_facebook.connect import connect_user
from open_facebook.api import FacebookAuthorization
import json
import datetime
import logging

from bidding.models import AuctionInvitation, Member, FBOrderInfo, BidPackage, Invitation
from bidding.views.auctions import get_auction_or_404
from bidding.views.home import render_response
from sslutils import get_protocol


logger = logging.getLogger('django')

def fb_redirect(request):
    response = HttpResponse("""<script type="text/javascript">
<!--
window.location = "%s"
//-->
</script>""" % (settings.NOT_AUTHORIZED_PAGE.format(protocol=get_protocol(request))))
    set_cookie(response, 'FBAPP_VISITED', 1, days_expire=7)
    return response
    #return HttpResponseRedirect('http://google.com')


def get_redirect_uri(request):
    """
    Returns the redirect uri to pass to facebook, using the correct protocol
    (http or https).
    """

    request_ids = ''
    if 'request_ids' in request.GET:
        request_ids = '?' + urlencode({'request_ids': request.GET['request_ids']})

    return settings.AUTH_REDIRECT_URI.format(
        protocol=get_protocol(request)) + request_ids


def fb_auth(request):
    """
    Redirects to Facebook to ask the user for giving authorization 
    to the app to access its personal information.
    Afterwards redirects to home page.
    """

    if request.user.is_authenticated():
    #Fix so admin user don't break on the root url
        try:
            request.user.get_profile()
        except Member.DoesNotExist:
            return HttpResponseRedirect(reverse('bidding_home'))

    url = settings.FACEBOOK_AUTH_URL.format(
        app=settings.FACEBOOK_APP_ID,
        url=get_redirect_uri(request))

    return render_response(request, 'fb_redirect.html', {'authorization_url': url})


def fb_test_user(request):
    token = FacebookAuthorization.get_app_access_token()
    test_user = FacebookAuthorization.create_test_user(token, 'email')

    connect_user(request, test_user['access_token'])

    #add bids by default
    member = request.user.get_profile()
    member.bids_left = 1000
    member.tokens_left = 1000
    member.save()

    return HttpResponseRedirect(reverse('bidding_home'))


def handle_invitations(request):
    """ Deletes pending FB user requests, and redirects to the last one. """

    request_ids = request.GET['request_ids'].split(',')

    invitation = None
    for request_id in request_ids:
        try:
            invitation = AuctionInvitation.objects.get(request_id=request_id)
            invitation.delete_facebook_request(request.user.get_profile())
        except AuctionInvitation.DoesNotExist:
            pass

    if not invitation:
        return HttpResponseRedirect(reverse('bidding_home'))

    return HttpResponseRedirect(reverse('bidding_auction_detail', args=
    (invitation.auction.item.slug,
     invitation.auction.id)))


def give_bids(request):
    member = request.user.get_profile()

    if not member.bids_left:
        member.bids_left = 500

    if not member.tokens_left:
        member.tokens_left = 1000

    member.save()


def fb_login(request):
    """
    Handles a facebook user's authentication and registering.
    Creates the user if it's not registered. Otherwise just logs in.
    """

    code = request.GET.get('code')
    if not code:
        #authorization denied
        return HttpResponseRedirect(settings.NOT_AUTHORIZED_PAGE)

    #try:
    token = FacebookAuthorization.convert_code(code, get_redirect_uri(request))['access_token']
    action, user = connect_user(request, token)

    #FIXME for test purposes
    #give_bids(request)

    if 'request_ids' in request.GET:
        return handle_invitations(request)

    return HttpResponseRedirect('/home/?aaa=2')


def store_invitation(request):
    auction = get_auction_or_404(request)
    member = request.user.get_profile()
    request_id = int(request.POST['request_id'])

    AuctionInvitation.objects.create(auction=auction, inviter=member,
                                     request_id=request_id).save()


def callback_get_items(request):
    """ Constructs the response to send item information to the FB dialog. """

    order_id = int(request.POST['order_info'])
    order = FBOrderInfo.objects.get(pk=order_id)
    package = order.package

    logger.debug("Entering callback_get_items")
    logger.debug("Package: %s" % package)

    image_url = settings.IMAGES_SITE + settings.MEDIA_URL + package.image.name

    response = {'method': 'payments_get_items',
                'content': [{'title': package.title,
                             'price': package.price,
                             'description': package.description,
                             'image_url': image_url,
                             'product_url': image_url,
                             'item_id': str(order.id)
                            }]}

    logger.debug("Returns %s" % response)
    return response


def callback_status_update(request):
    """ 
    Constructs the response to settle the payment. If the signed_request is 
    not validated, the payment is set as canceled.  
    """

    #checks that the request comes from Facebook
    if FacebookAuthorization.parse_signed_data(request.POST['signed_request']):
        details = json.loads(request.POST['order_details'])

        #order_id = details['order_info']
        #order = FBOrderInfo.objects.get(pk = order_id)
        #package =
        logger.debug(details)
        logger.debug(request.POST)
        order_id = int(details['items'][0]['item_id'])
        order = FBOrderInfo.objects.get(pk=order_id)
        package = order.package
        logger.debug("Pacakge: %s" % package)
        #package_id = int(details['items'][0]['item_id'])

        member = Member.objects.get(facebook_id=details['buyer'])
        member.bids_left += package.bids
        member.save()
        logger.debug("Member: %s" % member)

        order.status = 'confirmed'
        order.save()
        logger.debug("Order: %s" % order)

        return {'method': 'payments_status_update',
                'content': {'status': 'settled',
                            'order_id': request.POST['order_id']},
        }
    else:
        # TODO: If the order is canceled we should mark it as cancelled internally too
        return {'method': 'payments_status_update',
                'content': {'status': 'canceled',
                            'order_id': request.POST['order_id']},
        }


@csrf_exempt
def credits_callback(request):
    """ View for handling interaction with Facebook credits API. """

    response = {}

    logger.debug("credist_callback: %s" % request.POST['method'])

    if request.POST['method'] == 'payments_get_items':
        response = callback_get_items(request)

    elif (request.POST['method'] == 'payments_status_update' and
                  request.POST['status'] == 'placed'):
        response = callback_status_update(request)

    return HttpResponse(json.dumps(response), mimetype='text/javascript')


@csrf_exempt
def deauthorized_callback(request):
    """ View for handling the deauthorization callback.
    """

    if FacebookAuthorization.parse_signed_data(request.POST['signed_request']):
        user_id = json.load(request.POST['user_id'])
        member = get_object_or_404(Member, user_id)
        member.delete()
        request.session.flush()


@csrf_exempt
def place_order(request):
    """ View for placing an order from facebook credits
    """

    response = {'order_info': -1}
    if request.POST.has_key('package_id'):
        package = BidPackage.objects.get(pk=request.POST['package_id'])
        member = request.user.get_profile()
        status = 'placed'
        order = FBOrderInfo.objects.create(package=package,
                                           member=member,
                                           status=status,
        )
        response['order_info'] = order.id
    return HttpResponse(json.dumps(response), mimetype="text/javascript")


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                        secure=settings.SESSION_COOKIE_SECURE or None)

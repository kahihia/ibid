from urllib2 import urlopen
import json
import datetime
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
import django_facebook.connect
from django_facebook.models import FacebookLike

from bidding.models import AuctionInvitation, Member, FBOrderInfo, BidPackage, Item
from open_facebook.api import FacebookAuthorization
from open_facebook.exceptions import ParameterException, OAuthException

from bidding import client 
from bidding.models import ConfigKey
from bidding.views.home import render_response



logger = logging.getLogger('django')



def fb_redirect(request):
    return HttpResponseRedirect(reverse('bidding_anonym_home'))


def get_redirect_uri(request):
    """
    Returns the redirect uri to pass to facebook, using the correct protocol
    (http or https).
    """

    request_ids = ''
    if 'request_ids' in request.GET:
        request_ids = '?' + urlencode({'request_ids': request.GET['request_ids']})

    url = settings.FACEBOOK_AUTH_REDIRECT_URL.format(appname=settings.FACEBOOK_APP_NAME)

    return url + request_ids

def fb_test_user(request):
    token = FacebookAuthorization.get_app_access_token()
    test_user = FacebookAuthorization.create_test_user(token, 'email')

    django_facebook.connect.connect_user(request, test_user['access_token'])

    #add bids by default
    member = request.user
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
            invitation.delete_facebook_request(request.user)


        except AuctionInvitation.DoesNotExist:
            pass

    if not invitation:
        return HttpResponseRedirect(reverse('bidding_home'))

    return HttpResponseRedirect(reverse('bidding_auction_detail', args=
    (invitation.auction.item.slug,
     invitation.auction.id)))


def give_bids(request):
    member = request.user

    if not member.bids_left:
        member.bids_left = 500

    if not member.tokens_left:
        member.tokens_left = 1000

    member.save()

def fb_check_like(request):
    member = request.user
    response = False
    try:
        likes = member.fb_check_like()
        if likes:
            for like in likes['data']:
                if like['application']['name'] == settings.FACEBOOK_APP_NAME:
                    logger.debug(like['application']['name'])
                response = True
                break
    except Exception as e:
        raise
    return HttpResponse(json.dumps({'like':response,}))

def fb_like(request):
    member = request.user
    if request.method == 'POST':
        try:
            member.fb_like()
            like = member.likes()
            if not like:
                like = FacebookLike.objects.create(user_id = member.id,
                                                   facebook_id = member.facebook_id,
                                                   created_time = datetime.datetime.now())
                gift_tokens = ConfigKey.get('LIKE_GIFT_TOKENS', 1000)
                member.tokens_left += long(gift_tokens)
                member.save()
                return HttpResponse(
                    json.dumps({'info':'FIRST_LIKE',
                                'gift': gift_tokens,
                                'tokens': member.tokens_left,
                               }), content_type="application/json")
            return HttpResponse(
                json.dumps({'info':'NOT_FIRST_LIKE',
                            'gift': 0,
                            }), content_type="application/json")
        except OAuthException as e:
            if str(e).find('#3501') != -1:
                return HttpResponse(json.dumps({'info':'ALREADY_LIKE',}))
            #if str(e).find('#200') != -1:
            raise
    return HttpResponse(request.method)

def store_invitation(request):
    auction = get_auction_or_404(request)
    member = request.user
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
        logger.debug(details)
        logger.debug(request.POST)
        order_id = int(details['items'][0]['item_id'])
        order = FBOrderInfo.objects.get(pk=order_id)
        package = order.package
        logger.debug("Pacakge: %s" % package)

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
    fb_req=request.body
    logger.debug("Started FB payment callback: %s" % fb_req)
    
    payment = json.loads(fb_req)
    for elems in payment['entry']:
        url='https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (settings.FACEBOOK_APP_ID,settings.FACEBOOK_APP_SECRET)
        token=urlopen(url).read()
        url='https://graph.facebook.com/%s/?%s'%(elems['id'],token)
        pay_info=urlopen(url).read()
        payment_info =json.loads(pay_info)
        fid=payment_info['user']['id']
        status='completed'
        for it in payment_info['actions']:
            if it['status']!='completed':
                status ='not_completed'
        if status=='completed':
            member = Member.objects.get(facebook_id=fid)
            for it in payment_info['items']:
                id_prod=it['product'].split('/bid_package/')
                package = BidPackage.objects.get(pk=id_prod[1])
                order = FBOrderInfo.objects.create(package=package,
                                               member=member,
                                               fb_payment_id=payment_info['id']
                )
                member.bids_left += package.bids
                member.save()
                client.update_credits(member)
                logger.debug("FB payment callback, order: %s" % order.id)
            return HttpResponse()
    return HttpResponse('error')
    
def fb_item_info(request, item_id):
    item = Item.objects.get(pk=item_id)
    return render_response(request, "fb_item_info.html", {'item':item, 'url_domain':settings.WEB_APP})

def bid_package_info(request,package_id):
    package  = BidPackage.objects.get(pk= package_id)
    
    return render_response(request, "bid_package_info.html", {'package': package,'url_domain':settings.SITE_NAME})
    
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
        member = request.user
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


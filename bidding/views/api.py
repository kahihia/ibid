# -*- coding: utf-8 -*-

import json
import logging
import time

logger = logging.getLogger('django')

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from bidding import client
from bidding.models import Auction
from bidding.models import ConvertHistory
from bidding.models import Invitation
from bidding.models import Member
from bidding.models import ConfigKey
from bidding.models import FBOrderInfo
from bidding.views.facebook import post_story as fb_post_story
from chat import auctioneer
from chat.models import ChatUser
from chat.models import Message
from lib.utils import get_static_url


auction_type_id = ContentType.objects.filter(name='auction').all()[0]


def api(request, method):
    """api calls go through this method"""
    result = API[method](request)
    if type(result) is HttpResponse or result.__class__ == HttpResponse:
        return result
    else:
        return HttpResponse(result, content_type="application/json")


def getUserDetails(request):
    member = request.user

    data = {u'user':{
                u'displayName': member.display_name(),
                u'facebookId': member.facebook_id,
                u'profileFotoLink': member.display_picture(),
                u'profileLink': member.facebook_profile_url,
                u'credits': member.bids_left,
                u'tokens': member.tokens_left,
                u'username': member.username,
                u'email': member.email,
                u'first_name': member.first_name,
                u'last_name': member.last_name,
                u'won_auctions': Auction.objects.filter(winner=member).all().count(),
                u'actual_auctions': member.auction_set.exclude(status='waiting_payment').exclude(status='paid').all().count()
                
            },
            u'app':{
                u'tokenValueInCredits':settings.TOKENS_TO_BIDS_RATE,
                u'applink': settings.FACEBOOK_APP_URL.format(appname=settings.FACEBOOK_APP_NAME),
                u'apppicture': get_static_url('images/400x400-Fblogo.png'),
            }
        }

    return HttpResponse(json.dumps(data), content_type="application/json")

def getTemplateContext(request):
    data = {
        u'PUBNUB_PUB': settings.PUBNUB_PUB,
        u'PUBNUB_SUB': settings.PUBNUB_SUB,
        u'FB_APP_ID': settings.FACEBOOK_APP_ID,
        u'MIXPANEL_TOKEN': settings.MIXPANEL_TOKEN,
        u'SITE_NAME': settings.SITE_NAME,
        u'SITE_NAME_WOUT_BACKSLASH': settings.SITE_NAME_WOUT_BACKSLASH 
    }
    
    return HttpResponse(json.dumps(data), content_type="application/json")

def getAuctionsInitialization(request):
    member = request.user

    my_auctions = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid')).order_by(
        '-status').filter(bidders=member)
    other_auctions = Auction.objects.filter(is_active=True).exclude(
        status__in=('waiting_payment', 'paid', 'waiting', 'processing', 'pause')).order_by('-status').exclude(
        bidders=member)
    finished_auctions = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid', 'waiting', 'processing', 'pause')).filter(winner__isnull=False).order_by('-won_date')

    bids_auctions = {}
    tokens_auctions = {}

    other_auctions_limit = 10
    finished_limit = 10

    bids_auctions['my_auctions'] = my_auctions.filter(bid_type='bid')
    bids_auctions['other_auctions'] = other_auctions.filter(bid_type='bid')[:other_auctions_limit]
    bids_auctions['finished'] = finished_auctions.filter(bid_type='bid')[:finished_limit]

    tokens_auctions['my_auctions'] = my_auctions.filter(bid_type='token')
    tokens_auctions['other_auctions'] = other_auctions.filter(bid_type='token')[:other_auctions_limit]
    tokens_auctions['finished'] = finished_auctions.filter(bid_type='token')[:finished_limit]

    auctions_token_available = []
    auctions_token_finished = []
    auctions_token_my = []
    auctions_bid_available = []
    auctions_bid_finished = []
    auctions_bid_my = []

    for auct in tokens_auctions['other_auctions']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_token_available.append(tmp)

    for auct in bids_auctions['other_auctions']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['bidType'] = 'credit'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_bid_available.append(tmp)

    for auct in tokens_auctions['finished']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.first_name,
                         'displayName': auct.winner.display_name(),
                         'facebookId': auct.winner.facebook_id}
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_token_finished.append(tmp)

    for auct in bids_auctions['finished']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'credit'
        tmp['itemName'] = auct.item.name
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.first_name,
                         'displayName': auct.winner.display_name(),
                         'facebookId': auct.winner.facebook_id}
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_bid_finished.append(tmp)

    for auct in tokens_auctions['my_auctions']:
        tmp = {}

        tmp['id'] = auct.id
        if hasattr(auct, 'completion'):
            tmp['completion'] = auct.completion()
        else:
            tmp['completion'] = 0
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()
        
        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=True).order_by('-created')[:10]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=False).order_by('-created')[:10]:
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': auct.id
            }
            tmp['chatMessages'].insert(0, w)

        auctions_token_my.append(tmp)

    for auct in bids_auctions['my_auctions']:
        tmp = {}
        tmp['id'] = auct.id
        if hasattr(auct, 'completion'):
            tmp['completion'] = auct.completion()
        else:
            tmp['completion'] = 0
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'credit'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=True).order_by('-created')[:10]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=False).order_by('-created')[:10]:
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': auct.id
            }
            tmp['chatMessages'].insert(0, w)

        auctions_bid_my.append(tmp)

    data = {}
    data['token'] = {}
    data['token']['available'] = auctions_token_available
    data['token']['finished'] = auctions_token_finished
    data['token']['mine'] = auctions_token_my
    data['credit'] = {}
    data['credit']['available'] = auctions_bid_available
    data['credit']['finished'] = auctions_bid_finished
    data['credit']['mine'] = auctions_bid_my


    return HttpResponse(json.dumps(data), content_type="application/json")


def startBidding(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user

    try:
        amount = auction.minimum_precap
    except ValueError:
        return HttpResponse('{"success":"not int"}', content_type="application/json")

    if amount < auction.minimum_precap:
        return HttpResponse('{"success":"not minimun", "minimun": %s}' % auction.minimum_precap,
                            content_type="application/json")

    if auction.can_precap(member, amount):
        joining = auction.place_precap_bid(member, amount)
        if joining:
            pass

        clientMessages = []
        clientMessages.append(client.updatePrecapMessage(auction))
        clientMessages.append(auctioneer.member_joined_message(auction, member))
        client.sendPackedMessages(clientMessages)
    else:
        if auction.bid_type == 'bid':
            ret = {"success": False, 'motive': 'NO_ENOUGH_CREDITS'}
            return HttpResponse(json.dumps(ret), content_type="application/json")
        else:
            ret = {"success": False, 'motive': 'NO_ENOUGH_TOKENS'}
            return HttpResponse(json.dumps(ret), content_type="application/json")

    auct = auction
    tmp = {}

    tmp['id'] = auct.id
    if hasattr(auct, 'completion'):
        tmp['completion'] = auct.completion()
    else:
        tmp['completion'] = 0
    tmp['status'] = auct.status
    tmp['bidPrice'] = auct.minimum_precap
    tmp['bidType'] = {'token': 'token', 'bid': 'credit'}[auct.bid_type]
    tmp['itemName'] = auct.item.name
    tmp['retailPrice'] = str(auct.item.retail_price)
    tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
    tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
    tmp['placed'] = member.auction_bids_left(auct)
    tmp['bids'] = member.auction_bids_left(auct)
    tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
    tmp['bidders'] = auct.bidders.count()
    tmp['itemId'] = auct.item.id
    tmp['won_price'] = 0
    
    tmp['auctioneerMessages'] = []
    for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=True).order_by('-created')[:10]:
        w = {
            'text': mm.format_message(),
            'date': mm.get_time(),
            'auctionId': auct.id
        }
        tmp['auctioneerMessages'].append(w)

    tmp['chatMessages'] = []
    for mm in Message.objects.filter(object_id=auct.id).filter(_user__isnull=False).order_by('-created')[:10]:
        w = {'text': mm.format_message(),
             'date': mm.get_time(),
             'user': {'displayName': mm.get_user().display_name(),
                      'profileFotoLink': mm.get_user().picture(),
                      'profileLink': mm.get_user().user_link()},
             'auctionId': auct.id
        }
        tmp['chatMessages'].insert(0, w)

    ret = {"success": True, 'auction': tmp}
    return HttpResponse(json.dumps(ret), content_type="application/json")


def addBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user

    #minimum_precap means bid_price
    amount = auction.minimum_precap

    amount += member.auction_bids_left(auction)

    if auction.status == 'precap' and auction.can_precap(member, amount):
         #check max tokens for member per auction
        if auction.bid_type != 'bid' and (((amount*100)/(auction.precap_bids)) > ConfigKey.get('AUCTION_MAX_TOKENS', 100)):
            ret = {"success":False, 'motive': 'AUCTION_MAX_TOKENS_REACHED', 'data': {'placed': member.auction_bids_left(auction)}}
            return HttpResponse(json.dumps(ret), content_type="application/json")
        
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)
        success = True

        res = {'success': success, 'data': {'placed': member.auction_bids_left(auction)}}
        return HttpResponse(json.dumps(res), content_type="application/json")
    else:
        if auction.bid_type == 'bid':
            ret = {"success": False, 'motive': 'NO_ENOUGH_CREDITS',
                   'data': {'placed': member.auction_bids_left(auction)}}
            return HttpResponse(json.dumps(ret), content_type="application/json")
        else:
            ret = {"success": False, 'motive': 'NO_ENOUGH_TOKENS',
                   'data': {'placed': member.auction_bids_left(auction)}}
            return HttpResponse(json.dumps(ret), content_type="application/json")


def remBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    member = request.user
    #minimum_precap means bid_price
    amount = auction.minimum_precap

    amount = member.auction_bids_left(auction) - amount

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount, 'remove')

        client.updatePrecap(auction)

    if member.auction_bids_left(auction) > 0:
        res = {'success': True, 'data': {'placed': member.auction_bids_left(auction)}}
        return HttpResponse(json.dumps(res), content_type="application/json")
    else:
        return stopBidding(request)


def stopBidding(request):
    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user

    auction.leave_auction(member)

    clientMessages = []
    clientMessages.append(client.updatePrecapMessage(auction))
    clientMessages.append(auctioneer.member_left_message(auction, member))
    client.sendPackedMessages(clientMessages)

    ret = {'success': True, 'data': {'do': 'close'}}
    return HttpResponse(json.dumps(ret), content_type="application/json")



def claim(request):
    """
    The user uses the bids that has commit before to try to win the auction in
    process.
    """
    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.select_for_update().filter(id=auction_id)[0]
    #auction = Auction.objects.get(id=auction_id)
    bidNumber = request.GET.get('bidNumber', int(requPOST['bidNumber']))
    member = request.user

    tmp = {}
    tmp["success"] = False
    if auction.status == 'processing' and \
        auction.can_bid(member) and \
        auction.used_bids() / auction.minimum_precap == bidNumber:

        bid = auction.bid(member, bidNumber)
        auction.save()
        #bid = auction.bid_set.get(bidder=member)
        tmp['id'] = auction_id
        tmp["placed_amount"] = bid.placed_amount
        tmp["used_amount"] = bid.used_amount
        tmp["success"] = True

        clientMessages = []
        clientMessages.append(client.someoneClaimedMessage(auction))
        clientMessages.append(auctioneer.member_claim_message(auction, member))
        client.sendPackedMessages(clientMessages)
    return HttpResponse(json.dumps(tmp), content_type="application/json")


def reportAnError(request):
    """
    sends an email to us
    """
    member = request.user
    message = request.POST.get('message', '')
    gameState = request.POST.get('gameState', '{}')
    subject = settings.ERROR_REPORT_TITLE + ' - ' + member.facebook_name
    emailMessage = "message" + '\n' + message + '\n' + "gameState" + '\n' + gameState
    send_mail(subject, emailMessage, settings.DEFAULT_FROM_EMAIL, [tmp[1] for tmp in settings.ADMINS])
    return HttpResponse('', content_type="application/json")


def convertTokens(request):
    if request.method == "POST":
        member = request.user
        amount = member.maximun_bids_from_tokens()
        ConvertHistory.convert(member, int(amount))
        return HttpResponse('{"success":true}', content_type="application/json")
    return HttpResponse('{"success":false}', content_type="application/json")

def add_credits(request):
    if request.method == "POST":
        payment_id = int(request.POST['payment_id'])
        order = FBOrderInfo.objects.filter(fb_payment_id=payment_id)
        while not order:
            time.sleep(1)
            order = FBOrderInfo.objects.filter(fb_payment_id=payment_id)
        update_credits=order[0].member.bids_left
        return HttpResponse(
            json.dumps({'update_credits': update_credits,}),
            content_type="application/json")


def sendMessage(request):
    if request.method == 'POST':
        requPOST = json.loads(request.body)
        auction_id = request.GET.get('id', int(requPOST['id']))
        auction = Auction.objects.get(id=auction_id)

        text = request.GET.get('text', requPOST['text'])
        user_type_id = ContentType.objects.get(name='user')
        user = ChatUser.objects.get_or_create(object_id=request.user.id, content_type=user_type_id)[0]

        if user.can_chat(auction.id):
            db_msg = Message.objects.create(text=text, user=user, content_type=auction_type_id, object_id=auction.id)

            #do_send_message(db_msg)
            client.do_send_chat_message(auction, db_msg)

            return HttpResponse('{"success":true}', content_type="application/json")

    return HttpResponse('{"success":false}', content_type="application/json")


def inviteRequest(request):
    member = request.user

    requPOST = json.loads(request.body)
    invited = request.GET.get('invited', requPOST['invited'])

    client.log(str(invited))

    for fb_id in invited:
        #if already users or already invited: pass
        fb_id = int(fb_id)

        if len(Member.objects.filter(facebook_id=fb_id)) or len(Invitation.objects.filter(invited_facebook_id=fb_id)):
            pass
        #else: add to invited
        else:
            inv = Invitation()
            inv.inviter_id = member.id
            inv.invited_facebook_id = fb_id
            inv.save()

    return HttpResponse(json.dumps([True]))

def globalMessage(request):
    member = request.user
    if request.method == 'POST':
        requPOST = json.loads(request.body)
        text = requPOST['text']

        client.do_send_global_chat_message(member, text)

        return HttpResponse('{"success":true}', content_type="application/json")

    return HttpResponse('{"success":false}', content_type="application/json")

def post_story(auction, member):
    fb_post_story(auction, member)


API = {
    'startBidding': startBidding,
    'getAuctionsInitialization': getAuctionsInitialization,
    'addBids': addBids,
    'remBids': remBids,
    'claim': claim,
    'sendMessage': sendMessage,
    'getUserDetails': getUserDetails,
    'stopBidding': stopBidding,
    'reportAnError': reportAnError,
    'convertTokens': convertTokens,
    'inviteRequest': inviteRequest,
    'add_credits': add_credits,
    'globalMessage': globalMessage,
    'getTemplateContext' : getTemplateContext,
}

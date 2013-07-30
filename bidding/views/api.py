# -*- coding: utf-8 -*-

import json

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from bidding import client
from bidding.delegate import GlobalAuctionDelegate
from bidding.models import Auction
from bidding.models import AuctionFixture
from bidding.models import ConvertHistory
from bidding.models import Invitation
from bidding.models import Member
from chat import auctioneer
from chat.models import ChatUser
from chat.models import Message


def api(request, method):
    """api calls go through this method"""
    return API[method](request)


def getUserDetails(request):
    member = request.user.get_profile()

    data = {
        u'displayName': member.display_name(),
        u'facebookId': member.facebook_id,
        u'profileFotoLink': member.display_picture(),
        u'profileLink': member.facebook_profile_url,
        u'credits': member.bids_left,
        u'tokens': member.tokens_left
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


def getAuctionsInitialization(request):
    member = request.user.get_profile()

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
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name,
                         'displayName': auct.winner.get_profile().display_name(),
                         'facebookId': auct.winner.get_profile().facebook_id}
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
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name,
                         'displayName': auct.winner.get_profile().display_name(),
                         'facebookId': auct.winner.get_profile().facebook_id}
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        #tmp['won_price'] = str(auct.won_price)
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
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:10]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:10]:
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
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:10]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:10]:
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

    #auction_id = int(request.GET.get('id', int(request.POST.get('id', 0))))

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()

    try:
        amount = auction.minimum_precap
    except ValueError:
        return HttpResponse('{"result":"not int"}', content_type="application/json")

    if amount < auction.minimum_precap:
        return HttpResponse('{"result":"not minimun", "minimun": %s}' % auction.minimum_precap,
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
            ret = {"result":False, 'motive': 'NO_ENOUGH_CREDITS'}
            return HttpResponse(json.dumps(ret), content_type="application/json")
        else:
            ret = {"result":False, 'motive': 'NO_ENOUGH_TOKENS'}
            return HttpResponse(json.dumps(ret), content_type="application/json")

    ret = {"result":True}
    return HttpResponse(json.dumps(ret), content_type="application/json")


def addBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()

    #minimum_precap means bid_price
    amount = auction.minimum_precap

    amount += member.auction_bids_left(auction)

    if auction.status == 'precap' and auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)
        success = True

        res = {'success': success, 'data': {'placed': member.auction_bids_left(auction)}}
        return HttpResponse(json.dumps(res), content_type="application/json")
    else:
        if auction.bid_type == 'bid':
            ret = {"success":False, 'motive': 'NO_ENOUGH_CREDITS', 'data': {'placed': member.auction_bids_left(auction)}}
            return HttpResponse(json.dumps(ret), content_type="application/json")
        else:
            ret = {"success":False, 'motive': 'NO_ENOUGH_TOKENS', 'data': {'placed': member.auction_bids_left(auction)}}
            return HttpResponse(json.dumps(ret), content_type="application/json")



def remBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    #minimum_precap means bid_price
    amount = auction.minimum_precap

    amount = member.auction_bids_left(auction) - amount

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

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

    member = request.user.get_profile()

    auction.leave_auction(member)

    clientMessages = []
    clientMessages.append(client.updatePrecapMessage(auction))
    clientMessages.append(auctioneer.member_left_message(auction, member))
    client.sendPackedMessages(clientMessages)

    ret = {'success':True, 'data':{'do':'close'}}
    return HttpResponse(json.dumps(ret), content_type="application/json")


def claim(request):
    """
    The user uses the bids that has commit before to try to win the auction in
    process.
    """
    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.select_for_update().filter(id=auction_id)

    bidNumber = request.GET.get('bidNumber', int(requPOST['bidNumber']))

    member = request.user.get_profile()

    tmp = {}

    if auction.status == 'processing' and auction.can_bid(member):

        if auction.used_bids() / auction.minimum_precap == bidNumber:
            if auction.bid(member, bidNumber):

                clientMessages = []
                clientMessages.append(client.someoneClaimedMessage(auction))
                clientMessages.append(auctioneer.member_claim_message(auction, member))
                client.sendPackedMessages(clientMessages)

                bid = auction.bid_set.get(bidder=member)
                tmp['id'] = auction_id
                tmp["placed_amount"] = bid.placed_amount
                tmp["used_amount"] = bid.used_amount

                tmp["result"] = True
            else:
                #else ignore! because the claim is old, based on a previous timer.
                tmp["result"] = False
        else:
            #else ignore! because the claim is old, based on a previous timer.
            tmp["result"] = False
    else:
        tmp["result"] = False

    return HttpResponse(json.dumps(tmp), content_type="application/json")


def reportAnError(request):
    """
    sends an email to us
    """
    member = request.user.get_profile()
    message = request.POST.get('message', '')
    gameState = request.POST.get('gameState', '{}')
    subject = settings.ERROR_REPORT_TITLE + ' - ' + member.facebook_name
    emailMessage = "message" + '\n' + message + '\n' + "gameState" + '\n' + gameState
    send_mail(subject, emailMessage, settings.DEFAULT_FROM_EMAIL, [tmp[1] for tmp in settings.ADMINS])
    return HttpResponse('', content_type="application/json")


def convert_tokens(request):
    if request.method == "POST":
        requPOST = json.loads(request.body)
        amount = int(requPOST['amount'])

        member = request.user.get_profile()
        ConvertHistory.convert(member, int(amount))
        return HttpResponse(
            json.dumps({'tokens': member.get_bids("token"),
                        'bids': member.get_bids('bid'),
                        'maximun_bidsto': member.maximun_bids_from_tokens(),
                        'convert_combo': member.gen_available_tokens_to_bids(),
            }), content_type="application/json")


def sendMessage(request):
    if request.method == 'POST':
        requPOST = json.loads(request.body)
        auction_id = request.GET.get('id', int(requPOST['id']))
        auction = Auction.objects.get(id=auction_id)

        text = request.GET.get('text', requPOST['text'])
        user = ChatUser.objects.get_or_create(user=request.user)[0]

        if user.can_chat(auction):
            db_msg = Message.objects.create(text=text, user=user, auction=auction)

            #do_send_message(db_msg)
            client.do_send_chat_message(auction, db_msg)

            return HttpResponse('{"result":true}', content_type="application/json")

    return HttpResponse('{"result":false}', content_type="application/json")


def inviteRequest(request):
    member = request.user.get_profile()

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
    'convert_tokens': convert_tokens,
    'inviteRequest': inviteRequest,
}

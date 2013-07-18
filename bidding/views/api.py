# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail

from bidding import client
from bidding.models import Auction, ConvertHistory, Member, Invitation
from chat import auctioneer
from chat.models import Message, ChatUser

import json


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
        tmp['itemName'] = auct.item.name
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
        tmp['itemName'] = auct.item.name
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
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / settings.TODO_BID_PRICE if auct.status == 'processing' else 0
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:5]:
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
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / settings.TODO_BID_PRICE if auct.status == 'processing' else 0
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': auct.id
            }
            tmp['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:5]:
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
    data['TOKENS'] = {}
    data['TOKENS']['available'] = auctions_token_available
    data['TOKENS']['finished'] = auctions_token_finished
    data['TOKENS']['mine'] = auctions_token_my
    data['ITEMS'] = {}
    data['ITEMS']['available'] = auctions_bid_available
    data['ITEMS']['finished'] = auctions_bid_finished
    data['ITEMS']['mine'] = auctions_bid_my

    return HttpResponse(json.dumps(data), content_type="application/json")


def startBidding(request):
    """ The users commits bids before the auction starts. """

    #auction_id = int(request.GET.get('id', int(request.POST.get('id', 0))))

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    try:
        amount = settings.TODO_BID_PRICE
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

    return HttpResponse('{result: true}', content_type="application/json")

def addBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))

    amount += member.auction_bids_left(auction)

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)
        success = True
    else:
        success = False

    res = {'success': success}
    return HttpResponse(json.dumps(res), content_type="application/json")


def remBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))

    amount = member.auction_bids_left(auction) - amount

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)

    return HttpResponse('', content_type="application/json")


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

    return HttpResponse('', content_type="application/json")


def claim(request):
    """
    The user uses the bids that has commit before to try to win the auction in
    process.
    """
    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    bidNumber = request.GET.get('bidNumber', int(requPOST['bidNumber']))

    member = request.user.get_profile()

    tmp = {}

    if auction.status == 'processing' and auction.can_bid(member):

        if auction.used_bids() / settings.TODO_BID_PRICE == bidNumber:
            auction.bid(member)

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
    print "===============inviteRequest==============="
    member = request.user.get_profile()

    requPOST = json.loads(request.body)
    invited = request.GET.get('invited', requPOST['invited'])
    print invited

    client.log(str(invited))

    for fb_id in invited:
        #if already users or already invited: pass
        fb_id = int(fb_id)
        print fb_id, len(Member.objects.filter(facebook_id=fb_id)), len(Invitation.objects.filter(invited_facebook_id=fb_id))

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
    'getUserDetails': getUserDetails,
    'getAuctionsInitialization': getAuctionsInitialization,
    'startBidding': startBidding,
    'addBids': addBids,
    'remBids': remBids,
    'claim': claim,
    'stopBidding': stopBidding,
    'reportAnError': reportAnError,
    'convert_tokens': convert_tokens,
    'sendMessage': sendMessage,
    'inviteRequest': inviteRequest
}


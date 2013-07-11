# -*- coding: utf-8 -*-
from bidding.views.home import render_response

from django.conf import settings
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
import json

from bidding.models import Auction, Item, AuctionFixture, Member, ConvertHistory, PrePromotedAuction, PromotedAuction, Invitation
from chat.models import Message, ChatUser
from bidding.utils import send_member_left
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from chat.auctioneer import member_joined_message, member_left_message

from bidding import client

from chat import auctioneer

from django.core.mail import send_mail


def api(request, method ):
    """init info for the wiseDOM """
    #TODO try catch to avoid ugly error when admin is logged

    test = request.GET.get('test', 'asdasdasdasd')

    return API[method](request)


def getUserDetails(request):
    member = request.user.get_profile()

    data = {
        u'displayName':member.display_name(),
        u'facebook_id':member.facebook_id,
        u'profileFotoLink':member.display_picture(),
        u'profileLink':member.facebook_profile_url,
        u'credits':member.bids_left,
        u'tokens':member.tokens_left
        }

    return HttpResponse(json.dumps(data))

def getAuctionsInitialization(request):
    """init info for the wiseDOM """

    member = request.user.get_profile()

    my_auctions = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid')).order_by('-status').filter(bidders=member)
    other_auctions = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid', 'waiting', 'processing', 'pause')).order_by('-status').exclude(bidders=member)
    finished_auctions = Auction.objects.filter(is_active=True, status__in=('waiting_payment', 'paid', 'waiting', 'processing', 'pause')).filter(winner__isnull=False).order_by('-won_date')

    bids_auctions = {}
    tokens_auctions = {}

    other_auctions_limit = 5
    finished_limit = 5

    bids_auctions['my_auctions'] = my_auctions.filter(bid_type='bid')
    bids_auctions['other_auctions'] = other_auctions.filter(bid_type='bid')[:other_auctions_limit]
    bids_auctions['finished'] = finished_auctions.filter(bid_type='bid')[:finished_limit]

    tokens_auctions['my_auctions'] = my_auctions.filter(bid_type='token')
    tokens_auctions['other_auctions'] = other_auctions.filter(bid_type='token')[:other_auctions_limit]
    tokens_auctions['finished'] = finished_auctions.filter(bid_type='token')[:finished_limit]

    pre_promoted_auctions = PrePromotedAuction.objects.all() #.filter(is_active=True)
    promoted_auctions = PromotedAuction.objects.filter(promoter = member)

    auctions_token_available = []
    auctions_token_finished = []
    auctions_token_my = []
    auctions_bid_available = []
    auctions_bid_finished = []
    auctions_bid_my = []

    #data = {'id':bids_auctions['other_auctions'][0].id}

    for auct in tokens_auctions['other_auctions']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

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

        auctions_bid_available.append(tmp)

    for auct in tokens_auctions['finished']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name, 'displayName': auct.winner.get_profile().display_name(), 'facebookId':auct.winner.get_profile().facebook_id}

        auctions_token_finished.append(tmp)

    for auct in bids_auctions['finished']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name, 'displayName': auct.winner.get_profile().display_name(), 'facebookId':auct.winner.get_profile().facebook_id}

        #tmp['won_price'] = str(auct.won_price)
        auctions_bid_finished.append(tmp)

    for auct in tokens_auctions['my_auctions']:
        tmp = {}

        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['completion'] = auct.completion()
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
                'user':{'displayName': mm.get_user().display_name(),
                        'profileFotoLink': mm.get_user().picture(),
                        'profileLink': mm.user.user_link()},
                'auctionId': auct.id
                }
            tmp['chatMessages'].insert(0,w)



        auctions_token_my.append(tmp)

    for auct in bids_auctions['my_auctions']:
        tmp = {}
        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['completion'] = auct.completion()
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
                'user':{'displayName': mm.get_user().display_name(),
                        'profileFotoLink': mm.get_user().picture(),
                        'profileLink': mm.user.user_link()},
                'auctionId': auct.id
                }
            tmp['chatMessages'].insert(0,w)

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

    return HttpResponse(json.dumps(data))

def startBidding(request):
    """ The users commits bids before the auction starts. """

    #auction_id = int(request.GET.get('id', int(request.POST.get('id', 0))))

    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    try:
        amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))
    except ValueError:
        return HttpResponse('{"result":"not int"}')

    if amount < auction.minimum_precap:
        return HttpResponse('{"result":"not minimun", "minimun": %s}' % auction.minimum_precap)

    if auction.can_precap(member, amount):
        joining = auction.place_precap_bid(member, amount)
        if joining:
            pass

        client.updatePrecap(auction)

        auctioneer.member_joined_message(auction, member) #auctioneer message

    return HttpResponse('')



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

    res = {'success':success}
    return HttpResponse(json.dumps(res))


def remBids(request):
    """ The users commits bids before the auction starts. """

    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()
    amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))

    amount = member.auction_bids_left(auction)-amount

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)

    return HttpResponse('')

def stopBidding(request):
    requPOST = json.loads(request.body)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()

    auction.leave_auction(member)
    auctioneer.member_left_message(auction, member)

    client.updatePrecap(auction)

    return HttpResponse('')




def claim(request):
    """
    The user uses the bids that commited before to try to win the auction in
    process.
    """
    requPOST = json.loads(request.body)
    auction_id = request.GET.get('id', int(requPOST['id']))
    auction = Auction.objects.get(id=auction_id)

    bidNumber = request.GET.get('bidNumber', int(requPOST['bidNumber']))

    member = request.user.get_profile()

    tmp = {}

    if auction.status == 'processing' and auction.can_bid(member):

        if auction.used_bids()/settings.TODO_BID_PRICE == bidNumber:
            auction.bid(member)
            auctioneer.member_claim_message(auction, member)

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

    return HttpResponse(json.dumps(tmp))

def reportAnError(request):
    """
    sends an email to us
    """
    member = request.user.get_profile()

    message = request.POST.get('message', '')
    gameState = request.POST.get('gameState', '{}')


    subject = settings.ERROR_REPORT_TITLE + ' - ' + member.facebook_name

    emailMessage = "message"+'\n'+message+'\n'+"gameState"+'\n'+gameState
    send_mail(subject, emailMessage, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])


    return HttpResponse('')


def convert_tokens(request):
    if request.method == "POST":
        member = request.user.get_profile()
        ConvertHistory.convert(member, int(request.POST['amount']))
        return __member_status(member)

def sendMessage(request):
    if request.method == 'POST':
        requPOST = json.loads(request.body)
        auction_id = request.GET.get('id', int(requPOST['id']))
        auction = Auction.objects.get(id=auction_id)

        text = request.GET.get('text', requPOST['text'])
        user = get_chat_user(request)

        if user.can_chat(auction):
            db_msg = Message.objects.create(text=text, user=user, auction=auction)

            #do_send_message(db_msg)
            client.do_send_chat_message(auction,db_msg)

            return HttpResponse('{"result":true}')

    return HttpResponse('{"result":false}')


def get_chat_user(request):
    if not request.user.is_authenticated():
        raise Http404

    chat_user, _ = ChatUser.objects.get_or_create(user=request.user)
    return chat_user


def update_participants_page(request):
    #FIXME get_auction_or_404
    auction_id = int(request.POST['auction_id'])
    auction = Auction.objects.get(id=auction_id)
    page_number = int(request.POST['page'])
    page = participants_page(auction, page_number)

    content = render_to_string('bidding/detail/participants.html',
                               {'auction': auction, 'page' : page})
    data = json.dumps({'content' : content})
    return HttpResponse(data, mimetype='text/javascript')

def suggested_auction(user, current):
    """ Suggest an auction based on the product the user is browsing. """

    if not user.is_authenticated():
        return None

    member = user.get_profile()

    all_auctions = (Auction.objects.filter(status='precap').
                        exclude(id=current.id).exclude(bidders=member))

    if all_auctions:
        same_category = all_auctions.filter(item__category=current.item.category)

        if same_category:
            same_item = same_category.filter(item=current.item)
            return same_item[0] if same_item else same_category[0]

        return all_auctions[0]

    return None

def auction_detail(request, slug, id):
    auction = get_object_or_404(Auction, id=id)
    page = participants_page(auction, page_number=1)

    return render_response(request, 'bidding/detail/auction_detail.html',
        {'auction': auction, 'page' : page,
         'suggested' : suggested_auction(request.user, auction)})



@csrf_exempt
def auction_won_list(request):
    #FIXME ugly
    extra_query = ('(select count(*) from bidding_auctioninvoice '
                   'where bidding_auctioninvoice.status = %s '
                   'and bidding_auctioninvoice.auction_id=bidding_auction.id)')
    auctions = (Auction.objects.filter(winner=request.user)
                               .select_related('item')
                               .extra(select={'paid': extra_query},
                                      select_params=('paid',)))
    return render_response(request, 'bidding/auction_won_list.html',
        {'auctions': auctions})



def __member_status(member):
    return HttpResponse(
        json.dumps({'tokens': member.get_bids("token"),
                    'bids': member.get_bids('bid'),
                    'maximun_bidsto': member.maximun_bids_from_tokens(),
                    'convert_combo': member.gen_available_tokens_to_bids(),
                    }), mimetype="text/javascript")





import datetime

def set_cookie(response, key, value, days_expire = 7):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)





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
    'sendMessage': sendMessage
}


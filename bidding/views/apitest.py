# -*- coding: utf-8 -*-
from bidding.views.home import render_response

from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json

from bidding.models import Auction, Item, AuctionFixture, Member, ConvertHistory, PrePromotedAuction, PromotedAuction, Invitation
from chat.models import Message, ChatUser
from bidding.utils import send_member_left
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from chat.auctioneer import member_joined_message, member_left_message

from bidding import client

from chat import auctioneer


def apitest(request, method ):
    """init info for the wiseDOM """
    #TODO try catch to avoid ugly error when admin is logged

    test = request.GET.get('test', 'asdasdasdasd')

    return API[method](request)


def getUserDetails(request):
    member = request.user.get_profile()

    data = {
        u'displayName':member.display_name(),
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

    my_auctions = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid', 'waiting', 'processing', 'pause')).order_by('-status').filter(bidders=member)
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

    auctions_token_available = [] #[{u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pepe4', u'chat_enabled': False, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}],
    auctions_token_finished = [] #[{u'status': u'waiting_payment', u'title': u'pepe3', u'chat_enabled': False, u'last_bidder': u'ta-dah', u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0, u'won_price': 5}],
    auctions_token_my = [] #[{u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pepeasdasd', u'chat_enabled': True, u'chat_info': {u'user_pic': u'https://graph.facebook.com/100001640641493/picture', u'messages': [{u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'hola', u'user_name': u'Auctioneer'}, {u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'chau', u'user_name': u'Auctioneer'}], u'user_name': u'Daniel Nuske', u'id': 23}, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}, {u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pep2we', u'chat_enabled': True, u'chat_info': {u'user_pic': u'https://graph.facebook.com/100001640641493/picture', u'messages': [{u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'hola', u'user_name': u'Auctioneer'}, {u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'chau', u'user_name': u'Auctioneer'}], u'user_name': u'Daniel Nuske', u'id': 23}, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}]
    auctions_bid_available = [] #[{u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pepe4', u'chat_enabled': False, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}],
    auctions_bid_finished = [] #[{u'status': u'waiting_payment', u'title': u'pepe3', u'chat_enabled': False, u'last_bidder': u'ta-dah', u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0, u'won_price': 5}],
    auctions_bid_my = [] #[{u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pepeasdasd', u'chat_enabled': True, u'chat_info': {u'user_pic': u'https://graph.facebook.com/100001640641493/picture', u'messages': [{u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'hola', u'user_name': u'Auctioneer'}, {u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'chau', u'user_name': u'Auctioneer'}], u'user_name': u'Daniel Nuske', u'id': 23}, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}, {u'completion': 0, u'status': u'upcoming', u'tokens_or_bids_in_it': 0, u'bid_type': u'tokens', u'title': u'pep2we', u'chat_enabled': True, u'chat_info': {u'user_pic': u'https://graph.facebook.com/100001640641493/picture', u'messages': [{u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'hola', u'user_name': u'Auctioneer'}, {u'date': u'10/29/12 16:40', u'user_pic': u'/static/images/auctioneer_small.jpg', u'message': u'chau', u'user_name': u'Auctioneer'}], u'user_name': u'Daniel Nuske', u'id': 23}, u'bidders_count': 0, u'bids_left': 0, u'retail_price': 0, u'img_url': u'/media/cache/e7/7c/e77cc052833a6118e8752e462469c242.jpg', u'id': 0}]

    #data = {'id':bids_auctions['other_auctions'][0].id}

    for auct in tokens_auctions['other_auctions']:
        tmp = {}
        # tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        # tmp['bid_type'] = auct.bid_type
        # tmp['title'] = auct.item.name
        # tmp['chat_enabled'] = False
        # tmp['bidders_count'] = auct.bidders.count()
        #tmp['bids_left'] = member.auction_bids_left(auct)
        #tmp['retail_price'] = str(auct.item.retail_price)
        #tmp['img_url'] = auct.item.get_thumbnail()
        #tmp['minimum_precap'] = auct.minimum_precap

        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['completion'] = auct.completion()
        #tmp['placed'] = 9999
        #tmp['bids'] = 9999
        tmp['itemImage'] = auct.item.get_thumbnail()
        tmp['bidders'] = auct.bidders.count()

        auctions_token_available.append(tmp)

    for auct in bids_auctions['other_auctions']:
        tmp = {}
        # tmp['completion'] = auct.completion()
        # tmp['status'] = auct.status
        # tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        # tmp['bid_type'] = auct.bid_type
        # tmp['title'] = auct.item.name
        # tmp['chat_enabled'] = False
        # tmp['bidders_count'] = auct.bidders.count()
        # tmp['bids_left'] = member.auction_bids_left(auct)
        # tmp['retail_price'] = str(auct.item.retail_price)
        # tmp['img_url'] = auct.item.get_thumbnail()
        # tmp['id'] = auct.id
        # tmp['minimum_precap'] = auct.minimum_precap


        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['completion'] = auct.completion()
        #tmp['placed'] = 9999
        #tmp['bids'] = 9999
        tmp['itemImage'] = auct.item.get_thumbnail()
        tmp['bidders'] = auct.bidders.count()


        auctions_bid_available.append(tmp)

    for auct in tokens_auctions['finished']:
        tmp = {}
        # tmp['status'] = auct.status
        # tmp['title'] = auct.item.name
        # tmp['chat_enabled'] = False
        # tmp['retail_price'] = str(auct.item.retail_price)
        # tmp['img_url'] = auct.item.get_thumbnail()
        # tmp['last_bidder_profile'] = auct.winner.get_profile().facebook_profile_url
        # tmp['facebook_id'] = auct.winner.get_profile().facebook_id
        # tmp['id'] = auct.id
        # tmp['won_price'] = str(auct.won_price)

        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail()
        tmp['winner'] = auct.winner.get_profile().display_name()

        auctions_token_finished.append(tmp)

    for auct in bids_auctions['finished']:
        tmp = {}
        tmp['status'] = auct.status
        tmp['title'] = auct.item.name
        tmp['chat_enabled'] = False
        tmp['retail_price'] = str(auct.item.retail_price)
        tmp['img_url'] = auct.item.get_thumbnail()
        tmp['last_bidder'] = auct.winner.get_profile().display_name()
        tmp['last_bidder_profile'] = auct.winner.get_profile().facebook_profile_url
        tmp['facebook_id'] = auct.winner.get_profile().facebook_id
        tmp['id'] = auct.id
        tmp['won_price'] = str(auct.won_price)
        auctions_bid_finished.append(tmp)

    for auct in tokens_auctions['my_auctions']:
        tmp = {}
        # tmp['completion'] = auct.completion()
        # tmp['status'] = auct.status
        # tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        # tmp['bid_type'] = auct.bid_type
        # tmp['title'] = auct.item.name
        # tmp['chat_enabled'] = True
        # if tmp['chat_enabled']:
        #     messages = Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:5]
        #     tmp['chat_info'] = {'id': auct.id,
        #         'user_name': member.facebook_name,
        #         'user_pic':'https://graph.facebook.com/'+str(member.facebook_id)+'/picture',
        #         'messages': []}
        #     for mm in messages:
        #         w = {'user_name':mm.get_user().display_name(),
        #             'user_pic': mm.get_user().picture() ,
        #             'message': mm.format_message(),
        #             'user_link': mm.user.user_link(),
        #             'date': mm.get_time()
        #             }
        #         tmp['chat_info']['messages'].append(w)
        # tmp['auctioneer_enabled'] = True
        # if tmp['auctioneer_enabled']:
        #     messages = Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]
        #     tmp['auctioneer_info'] = {'messages': []}
        #     for mm in messages:
        #         w = {'user_name':mm.get_user().display_name(),
        #             'user_pic': mm.get_user().picture() ,
        #             'message': mm.format_message(),
        #             'date': mm.get_time()
        #             }
        #         tmp['auctioneer_info']['messages'].append(w)
        # tmp['bidders_count'] = auct.bidders.count()
        # tmp['bids_left'] = member.auction_bids_left(auct)
        # tmp['retail_price'] = str(auct.item.retail_price)
        # tmp['img_url'] = auct.item.get_thumbnail()
        # tmp['id'] = auct.id
        # tmp['minimum_precap'] = auct.minimum_precap

        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['completion'] = auct.completion()
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail()
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
            tmp['chatMessages'].append(w)



        auctions_token_my.append(tmp)

    for auct in bids_auctions['my_auctions']:
        tmp = {}
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        tmp['bid_type'] = auct.bid_type
        tmp['title'] = auct.item.name
        tmp['chat_enabled'] = bool(auct.message_set.count())
        tmp['chat_enabled'] = True
        if tmp['chat_enabled']:
            messages = Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:5]
            tmp['chat_info'] = {'id': auct.id,
                'user_name': member.facebook_name,
                'user_pic':'https://graph.facebook.com/'+str(member.facebook_id)+'/picture',
                'messages': []}
            for mm in messages:
                w = {'user_name':mm.get_user().display_name(),
                    'user_pic': mm.get_user().picture() ,
                    'message': mm.format_message(),
                    'user_link': mm.user.user_link(),
                    'date': mm.get_time()
                    }
                tmp['chat_info']['messages'].append(w)
        tmp['auctioneer_enabled'] = True
        if tmp['auctioneer_enabled']:
            messages = Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]
            tmp['auctioneer_info'] = {'messages': []}
            for mm in messages:
                w = {'user_name':mm.get_user().display_name(),
                    'user_pic': mm.get_user().picture(),
                    'message': mm.format_message(),
                    'date': mm.get_time()
                    }
                tmp['auctioneer_info']['messages'].append(w)
        tmp['bidders_count'] = auct.bidders.count()
        tmp['bids_left'] = member.auction_bids_left(auct)
        tmp['retail_price'] = str(auct.item.retail_price)
        tmp['img_url'] = auct.item.get_thumbnail()
        tmp['id'] = auct.id
        tmp['minimum_precap'] = auct.minimum_precap

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
            tmp['chatMessages'].append(w)

        auctions_bid_my.append(tmp)

    data = {}
    data['tokens'] = {}
    data['tokens']['available'] = auctions_token_available
    data['tokens']['finished'] = auctions_token_finished
    data['tokens']['mine'] = auctions_token_my
    data['credits'] = {}
    data['credits']['available'] = auctions_bid_available
    data['credits']['finished'] = auctions_bid_finished
    data['credits']['mine'] = auctions_bid_my

    return HttpResponse(json.dumps(data))

def startBidding(request):
    """ The users commits bids before the auction starts. """

    #auction_id = int(request.GET.get('id', int(request.POST.get('id', 0))))

    auction_id = int(request.GET.get('id'))
    auction = Auction.objects.get(id=auction_id)

    member_id = int(request.GET.get('memberId'))
    member = Member.objects.get(id=member_id)

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

    auction_id = int(request.GET.get('id'))
    auction = Auction.objects.get(id=auction_id)

    member_id = int(request.GET.get('memberId'))
    member = Member.objects.get(id=member_id)

    #member = request.user.get_profile()
    amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))

    amount += member.auction_bids_left(auction)

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)

    return HttpResponse('')


def remBids(request):
    """ The users commits bids before the auction starts. """

    auction_id = int(request.GET.get('id'))
    auction = Auction.objects.get(id=auction_id)

    member_id = int(request.GET.get('memberId'))
    member = Member.objects.get(id=member_id)

    amount = 5 #int(request.GET.get('amount', int(request.POST.get('amount', 0))))

    amount = member.auction_bids_left(auction)-amount

    if auction.can_precap(member, amount):
        auction.place_precap_bid(member, amount)

        client.updatePrecap(auction)

    return HttpResponse('')

def stopBidding(request):
    requPOST = json.loads(request.raw_post_data)
    auction_id = int(requPOST['id'])
    auction = Auction.objects.get(id=auction_id)

    member = request.user.get_profile()

    auction.leave_auction(member)
    auctioneer.member_left_message(auction, member)
    #send_member_left(auction, member)

    #update_user_data(member, auction)
    ##update_auction(auction)

    return HttpResponse('')

def wallpost(request):
    member = request.user.get_profile()

    args = {'name' : u'test',
            'caption' : u'yep',
            'link' : 'https://apps.facebook.com/interactivebids/',
            }
    return HttpResponse(str(member.post_to_wall(**args)))





def claim(request):
    """
    The user uses the bids that commited before to try to win the auction in
    process.
    """
    auction_id = int(request.GET.get('id'))
    auction = Auction.objects.get(id=auction_id)

    member_id = int(request.GET.get('memberId'))
    member = Member.objects.get(id=member_id)

    tmp = {}

    if auction.status == 'processing' and auction.can_bid(member):

        auction.bid(member)

        bid = auction.bid_set.get(bidder=member)
        tmp['id'] = auction_id
        tmp["placed_amount"] = bid.placed_amount
        tmp["used_amount"] = bid.used_amount

        auctioneer.member_claim_message(auction, member)



        tmp["result"] = True
    else:
        tmp["result"] = False


    return HttpResponse('')



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


def item_price(request):
    item_id = int(request.POST['item_id'])
    item = Item.objects.get(id=item_id)

    price = round(item.total_price or item.retail_price)

    return HttpResponse('{"price":%d}' % (price,))


def user_bids(request):
    member_id = int(request.POST['member_id'])
    member = Member.objects.get(id=member_id)
    return __member_status(member)


def run_fixture(request):
    fixture_id = int(request.POST['fixture_id'])
    AuctionFixture.objects.get(id=fixture_id).make_auctions()

    return HttpResponse('')

def item_info(request):
    term = request.REQUEST['term']
    items = Item.objects.filter(name__istartswith=term).values_list('name', flat=True)

    #why is this needed?
    items = [str(item) for item in items]

    return HttpResponse(json.dumps(items), mimetype='application/json')

def winners(request, page):
    auctions = (Auction.objects.filter(is_active=True, winner__isnull=False)
                               .annotate(current_price=Count('bid'))
                               .select_related('item', 'winner')
                               .order_by('-won_date'))
    return render_response(request, 'bidding/winners.html',
         {'auctions': auctions, 'current_page': page})

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

def auction_detail_update(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    details = json.dumps(render_details(auction))
    return HttpResponse(details, mimetype='text/javascript')

def sync_auction_timer(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    data = json.dumps({'auction_id' : auction.id,
                       'time' : auction.get_time_left()})
    return HttpResponse(data, mimetype='text/javascript')

def sync_timers(request):
    auctions = Auction.objects.filter(is_active=True,
                                      status__in=['processing', 'waiting'])

    def timers_dict(auction):
        return {'auction_id' : auction.id,
                'time' : auction.get_time_left()}

    auctions = map(timers_dict, auctions)

    return HttpResponse(json.dumps(auctions), mimetype='text/javascript')


def __member_status(member):
    return HttpResponse(
        json.dumps({'tokens': member.get_bids("token"),
                    'bids': member.get_bids('bid'),
                    'maximun_bidsto': member.maximun_bids_from_tokens(),
                    'convert_combo': member.gen_available_tokens_to_bids(),
                    }), mimetype="text/javascript")


def convert_tokens(request):
    if request.method == "POST":
        member = request.user.get_profile()
        ConvertHistory.convert(member, int(request.POST['amount']))
        return __member_status(member)


def create_promoted(request):
    request.POST['pre_promoted_id']
    request.POST['facebook_user_id']

    pre_promoted_auction = PrePromotedAuction.objects.filter(is_active=True, id=request.POST['pre_promoted_id'])

    if len(pre_promoted_auction) <> 1:
        return error
    else:
        pre_promoted_auction = pre_promoted_auction[0]

    pa = PromotedAuction(
        promoter = Member.objects.filter(facebook_id = request.POST['facebook_user_id'])[0],
        item = pre_promoted_auction.item,
        precap_bids = pre_promoted_auction.precap_bids,
        minimum_precap = pre_promoted_auction.minimum_precap,
        bid_type = pre_promoted_auction.bid_type,
        status = pre_promoted_auction.status,
        bidding_time = pre_promoted_auction.bidding_time,
        saved_time = pre_promoted_auction.saved_time,
        threshold1 = pre_promoted_auction.threshold1,
        threshold2 = pre_promoted_auction.threshold2,
        threshold3 = pre_promoted_auction.threshold3,
        is_active = True
    )
    pa.save()

    return HttpResponseRedirect('/')

def redirect_promoted(request, auction_id):
    #check if the auction exists
    auction = get_object_or_404(Auction, id=auction_id)

    #save cookie to visit an auction
    request.session['redirect_to'] = '/promoted_redirected/%s' % str(auction_id)

    #redirects to home so it enters to fb fb app
    res = HttpResponseRedirect('/')

    return res


import datetime

def set_cookie(response, key, value, days_expire = 7):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)







def split_member_auctions(member, auction_list):
    """
    Takes a list of auctions an returns a sublist of the auctions the member
    has joined, and a sublist with 5 auctions the user hasn't joined.
    """

    mine = auction_list.filter(bidders=member)
    other = auction_list.exclude(bidders=member)

    return mine, other


def split_bid_type(queryset, bids_auctions, tokens_auctions, key, limit=None):
    """
    Takes an auction queryset and splits it in token and bid auctions, putting
    it in the correct dict under the given key.
    """

    bids_auctions[key] = queryset.filter(bid_type='bid')
    tokens_auctions[key] = queryset.filter(bid_type='token')

    if limit:
        bids_auctions[key] = bids_auctions[key][:limit]
        tokens_auctions[key] = tokens_auctions[key][:limit]


API = {
    'getUserDetails': getUserDetails,
    'getAuctionsInitialization': getAuctionsInitialization,
    'startBidding': startBidding,
    'addBids': addBids,
    'remBids': remBids,
    'claim': claim,
    'stopBidding': stopBidding,
    'wallpost': wallpost
}


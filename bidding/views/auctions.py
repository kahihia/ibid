# -*- coding: utf-8 -*-
from routines.shortcuts import render_response

from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json

from bidding.models import Auction, Item, AuctionFixture, Member, ConvertHistory, PrePromotedAuction, PromotedAuction
from bidding.utils import render_details, send_member_left
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from chat.auctioneer import member_joined_message, member_left_message
from chat import auctioneer

from bidding import client

from chat.models import Message, ChatUser




def get_auction_or_404(request):
    """
    Gets the auction id from the POST dict and returns the matching auction.
    If it's not found, Http404 is raised.
    """
    if request.GET and request.user.is_authenticated():
        auction_id = request.GET.get('auction_id')
        if auction_id:
            return get_object_or_404(Auction, id=auction_id)
    elif request.POST and request.user.is_authenticated():
        auction_id = request.POST.get('auction_id')
        if auction_id:
            return get_object_or_404(Auction, id=auction_id)

    raise Http404

def precap_bid(request):
    """ The users commits bids before the auction starts. """
    
    auction = get_auction_or_404(request)
    member = request.user.get_profile()
    try:
        amount = int(request.GET.get('amount', int(request.POST.get('amount', 0))))
    except ValueError:
        return HttpResponse('{"result":"not int"}')
    
    if amount < auction.minimum_precap:
        return HttpResponse('{"result":"not minimun", "minimun": %s}' % auction.minimum_precap)
    
    if auction.can_precap(member, amount):
        joining = auction.place_precap_bid(member, amount)
        if joining:
            auctioneer.member_joined_message(auction, member) #auctioneer message
        
        client.updatePrecap(auction)
        
        return HttpResponse(json.dumps({"result":True,
                                        "bids": member.get_bids_left(),
                                        "tokens" : member.get_tokens_left(),
                                        "maximun_bidsto": member.maximun_bids_from_tokens(),
                                        }))
    if auction.bid_type == "token":
        return HttpResponse('{"result":"no_tokens"}')
    return HttpResponse('{"result":"no_bids"}')

def first_precap(request):
    """ The users commits bids before the auction starts. """
    
    auction = get_auction_or_404(request)
    member = request.user.get_profile()
    try:
        amount = int(request.GET.get('amount', int(request.POST.get('amount', 0))))
    except ValueError:
        return HttpResponse('{"result":"not int"}')
    
    if amount < auction.minimum_precap:
        return HttpResponse('{"result":"not minimun", "minimun": %s}' % auction.minimum_precap)
    
    if auction.can_precap(member, amount):
        joining = auction.place_precap_bid(member, amount)
        
        
        if joining:
            auctioneer.member_joined_message(auction, member) #auctioneer message
            #send_member_joined(auction, member) 
            
        
        #update_user_data(member, auction)  #not needed, managed from JS 
        client.updatePrecap(auction)
        
    #reload the auction so it takes the new state
    auction.save()
    auct = get_object_or_404(Auction, id=auction.id)

    member = request.user.get_profile()

    tmp = {}

    if auct.status == 'precap':

        #elif atype == 'my':
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        tmp['bid_type'] = auct.bid_type
        tmp['title'] = auct.item.name
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
                    'date': mm.get_time()
                    }
                tmp['chat_info']['messages'].append(w)
        tmp['auctioneer_enabled'] = True
        if tmp['auctioneer_enabled']:
            messages = Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]
            tmp['auctioneer_info'] = {'messages': []}
            for mm in messages:
                w = {'user_name':mm.get_user().display_name(),
                    'user_pic': mm.get_user().picture() ,
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

    else:

        #elif atype == 'my':
        tmp['completion'] = '100'
        tmp['status'] = auct.status
        tmp['tokens_or_bids_in_it'] = member.auction_bids_left(auct)
        tmp['bid_type'] = auct.bid_type
        tmp['title'] = auct.item.name
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
                    'date': mm.get_time()
                    }
                tmp['chat_info']['messages'].append(w)
        tmp['auctioneer_enabled'] = True
        if tmp['auctioneer_enabled']:
            messages = Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:5]
            tmp['auctioneer_info'] = {'messages': []}
            for mm in messages:
                w = {'user_name':mm.get_user().display_name(),
                    'user_pic': mm.get_user().picture() ,
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



    tmp['result'] = True
    tmp['bids'] = member.get_bids_left()
    tmp['tokens'] = member.get_tokens_left()



    return HttpResponse(json.dumps(tmp))



def leave_auction(request):
    auction = get_auction_or_404(request)
    member = request.user.get_profile()
    
    auction.leave_auction(member)
    auctioneer.member_left_message(auction, member)
    send_member_left(auction, member)
    
    #update_user_data(member, auction)
    ##update_auction(auction)
    
    return HttpResponse('{"result":true, "bids":%d, "tokens" : %d}' % 
                                                (member.get_bids_left(), member.get_tokens_left()))
    

def bid(request):
    """ 
    The user uses the bids that commited before to try to win the auction in 
    process. 
    """
    auction = get_auction_or_404(request)
    member = request.user.get_profile()

    tmp = {}
    
    if auction.status == 'processing' and auction.can_bid(member):

        auction.bid(member)


        tmp["result"] = True
    else:
        tmp["result"] = False
    bid = auction.bid_set.get(bidder=member)
    tmp["bids_left"] = bid.placed_amount - bid.used_amount
    tmp["placed_amount"] = bid.placed_amount
    tmp["used_amount"] = bid.used_amount

    return HttpResponse(json.dumps(tmp))


def participants_page(auction, page_number):
    paginator = Paginator(auction.bidders.all(), 8)
    return paginator.page(page_number)

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
    for auction in auctions:
        auction.winner_member = Member.objects.filter(user__id=auction.winner.id)[0]
    #return render_response(request, 'bidding/winners.html',{'auctions': auctions, 'current_page': page})
    return render_response(request, 'bidding/ibidgames_winners.html',{'auctions': auctions, 'current_page': page})

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


'''
Browse auctions views.
'''
from bidding import models
from routines.shortcuts import render_response
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import simplejson as json
from django.template.context import RequestContext
from bidding.models import ITEM_CATEGORY_CHOICES
from django.utils.datastructures import SortedDict
from django.db.models import Q
from django.db.models.aggregates import Count

STATUS_FILTERS = SortedDict()
STATUS_FILTERS['All auctions'] = lambda qs, member: qs.order_by('status')
STATUS_FILTERS['My auctions'] = lambda qs, member: qs.filter(
                                            bidders=member).order_by('status') 
STATUS_FILTERS['Running'] = lambda qs, member: qs.filter(status='processing'
                                                    ).order_by('-start_date')
STATUS_FILTERS['Upcoming'] = lambda qs, member: qs.filter(
                                            status__in=('precap', 'waiting')
                                            ).annotate(bidders_count=Count('bidders')
                                                ).order_by('-bidders_count') 
STATUS_FILTERS['Finished'] = lambda qs, member: qs.filter(
                                            status__in=('waiting_payment',
                                                        'paid'))

ALL_CATEGORIES = 'All categories'
CATEGORY_CHOICES = [ALL_CATEGORIES] + [choice[1] for choice in ITEM_CATEGORY_CHOICES]

def filter_category(auctions, category):
    if category == ALL_CATEGORIES:
        return auctions
    
    for choice in ITEM_CATEGORY_CHOICES:
        if choice[1] == category:
            return auctions.filter(item__category=choice[0])

def filter_term(auctions, term):
    
    if not term:
        return auctions
    
    return auctions.filter(Q(item__name__icontains=term) |
            Q(winner__first_name__icontains=term) | 
            Q(winner__last_name__icontains=term))

def filter_auctions(request, bid_type):
    auctions = models.Auction.objects.filter(
                            is_active=True).filter(bid_type=bid_type)
    
    #filter status
    status = request.REQUEST.get('status', 'All auctions')
    auctions = STATUS_FILTERS[status](auctions, request.user.get_profile())
    
    #filter categories
    category = request.REQUEST.get('category', ALL_CATEGORIES)
    auctions = filter_category(auctions, category) 
    
    #filter term
    term = request.REQUEST.get('term', '').strip()
    auctions = filter_term(auctions, term)
    
    return auctions


def get_auctions_page(request, bid_type, page_number):
    auctions = filter_auctions(request, bid_type)
                            
    return Paginator(auctions, 10).page(page_number)


def browse_auctions(request):
    return render_response(request, 'bidding/browse.html',
        {'bids_page' : get_auctions_page(request, 'bid', 1),
         'tokens_page' : get_auctions_page(request, 'token', 1),
         'status_choices' : STATUS_FILTERS.keys(),
         'category_choices' : CATEGORY_CHOICES,
         'status' : request.REQUEST.get('status'),
         'term' : request.REQUEST.get('term', ''),
         })

def update_browse_page(request):
    bid_type = request.POST['bid_type']
    page_number = request.POST['page_number']
    
    page = get_auctions_page(request, bid_type, page_number)
    
    content = render_to_string('bidding/browse_auction_list.html',
                               {'page' : page, 'bid_type' : bid_type},
                               RequestContext(request))
    
    data = json.dumps({'content' : content, 'bid_type' : bid_type})
    return HttpResponse(data, mimetype='text/javascript')
    
def search_autocomplete(request):
    term = request.GET.get('term', '').strip()
    item_names = models.Auction.objects.filter(item__name__icontains=term
                                        ).values_list('item__name', flat=True)
    
    winner_first_names = models.Auction.objects.filter(
                                        winner__first_name__icontains=term
                                        ).values_list('winner__first_name', 
                                                      flat=True)
    
    winner_last_names = models.Auction.objects.filter(
                                        winner__last_name__icontains=term
                                        ).values_list('winner__last_name', 
                                                      flat=True)
    
    item_names = list(set(map(str, item_names)) |
                      set(map(str, winner_first_names)) |
                      set(map(str, winner_last_names)))
                                                                             
    return HttpResponse(json.dumps(item_names), mimetype='application/json')

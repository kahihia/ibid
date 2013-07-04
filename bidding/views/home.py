'''
Home page views.
'''
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, Http404, HttpResponse
from bidding.models import Auction, ConvertHistory, PrePromotedAuction, PromotedAuction
from django.core.urlresolvers import reverse
from django.conf import settings
from bidding.models import BidPackage

from django.contrib.flatpages.models import FlatPage

from settings import CANVAS_HOME


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


def mainpage(request):
    return HttpResponse("""<script type='text/javascript'>
    top.location.href = '""" + CANVAS_HOME + """';
 </script>""")


def canvashome(request):
    #if redirect cookie
    #return HttpResponse("request.user.is_authenticated()" + str(request.user.is_authenticated()))

    redirectTo = request.session.get('redirect_to', False)
    if redirectTo:
        del request.session['redirect_to']
        return HttpResponseRedirect(str(redirectTo))

    #return HttpResponse('request.user.is_authenticated(): '+str(request.user.is_authenticated()))

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('bidding_anonym_home'))

    #TODO try catch to avoid ugly error when admin is logged
    member = request.user.get_profile()

    bids_auctions = {}
    tokens_auctions = {}

    display_popup = False
    if not request.session.get("revisited"):
        request.session["revisited"] = True
        display_popup = True

    if request.COOKIES.get('dont_show_welcome_%s' %
            request.user.get_profile().facebook_id):
        display_popup = False

    active = Auction.objects.filter(is_active=True).exclude(status__in=(
        'waiting_payment', 'paid')
    ).order_by('-status')

    my_auctions, other_auctions = split_member_auctions(member, active)
    split_bid_type(my_auctions, bids_auctions, tokens_auctions, 'my_auctions')
    split_bid_type(other_auctions, bids_auctions, tokens_auctions, 'other_auctions', 5)

    finished = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid')
    ).order_by('-won_date')
    split_bid_type(finished, bids_auctions, tokens_auctions, 'finished', 5)

    has_played = bool(Auction.objects.filter(bidders=member))

    pre_promoted_auctions = PrePromotedAuction.objects.all() #.filter(is_active=True)
    promoted_auctions = PromotedAuction.objects.filter(promoter=member)

    tosintro = FlatPage.objects.filter(title="tacintro")[0].content

    packages = BidPackage.objects.all().order_by('bids')

    response = render_response(request, 'bidding/mainpage.html',
                               {'fb_app_id': settings.FACEBOOK_APP_ID, 'PUBNUB_PUB': settings.PUBNUB_PUB,
                                'PUBNUB_SUB': settings.PUBNUB_SUB, 'bids_auctions': bids_auctions,
                                'tokens_auctions': tokens_auctions,
                                'has_played': has_played, 'display_popup': display_popup,
                                'pre_promoted_auctions': pre_promoted_auctions, 'facebook_user_id': member.facebook_id,
                                'promoted_auctions': promoted_auctions, 'tosintro': tosintro, 'member': member, 'packages':packages})

    return response


def faq(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('bidding_anonym_home'))

    member = request.user.get_profile()

    if not request.session.get("revisited"):
        request.session["revisited"] = True

    response = render_response(request, 'bidding/ibidgames_faq.html',
                               {'PUBNUB_PUB': settings.PUBNUB_PUB, 'PUBNUB_SUB': settings.PUBNUB_SUB,
                                'facebook_user_id': member.facebook_id})

    return response


def promoted(request, auction_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('bidding_anonym_home'))

    #TODO try catch to avoid ugly error when admin is logged
    member = request.user.get_profile()

    bids_auctions = {}
    tokens_auctions = {}

    display_popup = False
    if not request.session.get("revisited"):
        request.session["revisited"] = True
        display_popup = True

    if request.COOKIES.get('dont_show_welcome_%s' %
            request.user.get_profile().facebook_id):
        display_popup = False

    pre_promoted_auctions = PrePromotedAuction.objects.all() #.filter(is_active=True)
    view_promoted_auction = PromotedAuction.objects.filter(id=auction_id)[0]
    active = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid')).exclude(
        id__in=[p.id for p in PromotedAuction.objects.all()]).order_by('-status')

    my_auctions, other_auctions = split_member_auctions(member, active)
    split_bid_type(my_auctions, bids_auctions, tokens_auctions, 'my_auctions')
    split_bid_type(other_auctions, bids_auctions, tokens_auctions, 'other_auctions', 5)

    finished = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid')
    ).order_by('-won_date')
    split_bid_type(finished, bids_auctions, tokens_auctions, 'finished', 5)

    has_played = bool(Auction.objects.filter(bidders=member))

    return render_response(request, 'bidding/mainpage_promoted.html',
                           {'bids_auctions': bids_auctions, 'tokens_auctions': tokens_auctions,
                            'has_played': has_played, 'display_popup': display_popup,
                            'facebook_user_id': member.facebook_id, 'view_promoted_auction': view_promoted_auction})


def web_home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.FBAPP)
        #return HttpResponse("""<script type='text/javascript'>
        #top.location.href = '""" + CANVAS_HOME + """';
        #</script>""")

    else:
        if request.COOKIES.get('FBAPP_VISITED'):
            return HttpResponseRedirect(settings.FBAPP)
        else:
            return HttpResponse("""<script type='text/javascript'>
        top.location.href = '""" + settings.APP_FIRST_REDIRECT + """';
        </script>""")

def history(request):
    member = request.user.get_profile()
    return render_response(request, "bidding/history.html", {'history': member.bids_history()})


class CurrencyHistory(ListView):
    paginated_by = settings.PAGINATED_BY
    template_name = "bidding/history.html"

    def get_queryset(self):
        return ConvertHistory.objects.filter(member=self.request.user.get_profile())


from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)



def winner_email_example(request):
    #if redirect cookie
    #return HttpResponse("request.user.is_authenticated()" + str(request.user.is_authenticated()))

    redirectTo = request.session.get('redirect_to', False)
    if redirectTo:
        del request.session['redirect_to']
        return HttpResponseRedirect(str(redirectTo))

    #return HttpResponse('request.user.is_authenticated(): '+str(request.user.is_authenticated()))

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('bidding_anonym_home'))

    #TODO try catch to avoid ugly error when admin is logged

    finished = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid')
    ).order_by('-won_date')

    auction = finished[0]
    user = request.user

    if user and  auction.bid_type == 'bid':
        print "sending email"

        response = render_response(request, 'bidding/mail_winner.html',
                                   {'user' : user,
                                    'auction' : auction,
                                    'site': settings.SITE_NAME,
                                    'images_site':settings.IMAGES_SITE})


    return response

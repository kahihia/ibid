'''
Home page views.
'''

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.list import ListView

from bidding.models import Auction, ConvertHistory

def mainpage(request):
    return HttpResponse("""<script type='text/javascript'>
    top.location.href = '""" + settings.CANVAS_HOME + """';
 </script>""")


def canvashome(request):

    redirectTo = request.session.get('redirect_to', False)
    if redirectTo:
        del request.session['redirect_to']
        return HttpResponseRedirect(str(redirectTo))

    #TODO try catch to avoid ugly error when admin is logged
    member = request.user.get_profile()

    #give free tokens from promo
    freeExtraTokens = request.session.get('freeExtraTokens', 0)
    if freeExtraTokens and not member.getSession('freeExtraTokens', None):
        member.tokens_left += freeExtraTokens
        member.setSession('freeExtraTokens', 'used')
        print " ----------- member session", member.session
        member.save()
        del request.session['freeExtraTokens']

    display_popup = False
    if not request.session.get("revisited"):
        request.session["revisited"] = True
        display_popup = True

    if request.COOKIES.get('dont_show_welcome_%s' %
            request.user.get_profile().facebook_id):
        display_popup = False

    response = render_response(request, 'bidding/mainpage.html',
                               {'fb_app_id': settings.FACEBOOK_APP_ID,
                                'PUBNUB_PUB': settings.PUBNUB_PUB,
                                'PUBNUB_SUB': settings.PUBNUB_SUB,
                                'display_popup': display_popup,
                                'facebook_user_id': member.facebook_id,
                                'tosintro': FlatPage.objects.filter(title="tacintro")[0].content,
                                'member': member})

    return response

def promo(request):
    print "promo_redirect", request.session.get('promo_redirect')

    promoCode = request.GET.get('promoCode', None)
    if promoCode:
        request.session['freeExtraTokens'] = 2000
        return HttpResponseRedirect(settings.WEB_APP)

    response = render_response(request, 'bidding/promo.html',
                               {'promo_url': settings.WEB_APP+'promo/'})
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


def web_home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.FBAPP)
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
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('bidding_anonym_home'))

    finished = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid')
    ).order_by('-won_date')

    auction = finished[0]
    user = request.user

    response = render_response(request, 'bidding/mail_winner.html',
                               {'user' : user,
                                'auction' : auction,
                                'site': settings.SITE_NAME,
                                'images_site':settings.IMAGES_SITE})

    return response

def example_404(request):
    response = render_response(request, '404.html')
    return response

def example_500(request):
    response = render_response(request, '500.html')
    return response


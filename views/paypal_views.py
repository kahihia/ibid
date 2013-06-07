from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from routines.shortcuts import render_response

from django.conf import settings
from bidding.models import BidPackage, AuctionInvoice, Auction
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404

@login_required
def buy_item(request, id):
    auction = get_object_or_404(Auction, id=id)
    
    if auction.status != 'waiting_payment' or request.user != auction.winner:
        raise Http404
    
    invoice = get_object_or_404(AuctionInvoice, auction=auction)
    
    domain = settings.SITE_NAME
    item = {
        'amount': float(auction.won_price),
        'invoice': invoice.uid,
        'item_name': auction.item.name,
        'item_number': auction.item.id,
        'custom': 'item;%d' % request.user.id,
        "cancel_url": '%s/' % domain,
        #"return_url": '%s' % domain,
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        "notify_url": '%s/paypal/ipn/' % domain,
        'no_shipping' : 0,
    }
    form = PayPalPaymentsForm(initial=item)
    return render_response(request, 'bidding/buy_item.html',
         {'form': form, 'auction': auction})


import json
import logging
import datetime


from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import payment_was_successful 
from bidding.views.home import render_response
from bidding import client
from bidding.models import BidPackage, AuctionInvoice, Auction,buy_tokens,PaypalPaymentInfo,Member,Item
   

logger = logging.getLogger('django')

def buy_item(request, id):
    if  request.user.is_authenticated():
        auction = get_object_or_404(Auction, id=id)
    
        if request.user != auction.winner:
            raise Http404
        elif auction.status == 'waiting_payment':
    
            invoice = get_object_or_404(AuctionInvoice, auction=auction)
    
            domain = settings.SITE_NAME
            item = {
                'amount': float(auction.won_price),
                'invoice': invoice.uid,
                'item_name': auction.item.name,
                'item_number': auction.item.id,
                "custom": '{"member_id":%s}' %(request.user.id),
                "cancel_url": '%s/' % domain,
                #"return_url": '%s' % domain,
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                "notify_url": '%s/paypal/ipn/' % domain,
                'no_shipping' : 0,
            }
            form = PayPalPaymentsForm(initial=item)
            return render_response(request, 'bidding/buy_item.html',
                 {'form': form, 'auction': auction})
        elif auction.status == 'paid':
    
            domain = settings.SITE_NAME
            return render_response(request, 'bidding/buy_item.html',
                 {'auction': auction})
    else:
        request.session['redirect_to'] = request.get_full_path()
        return HttpResponseRedirect(reverse('fb_auth'))
        

def payment_callback(sender, **kwargs):
    logger.debug("in callback")
    ipn_obj = sender
    if ipn_obj.payment_status == "Completed":
        custom_params=json.loads(str(ipn_obj.custom))
        member = Member.objects.get(id=custom_params['member_id'])
        if 'package_id' in custom_params:
            package = BidPackage.objects.get(pk=custom_params['package_id'])
            order = PaypalPaymentInfo.objects.create(package=package,member=member,transaction_id =ipn_obj.txn_id,quantity=1,purchase_date=datetime.datetime.now())
            member.bids_left += package.bids
            member.save()
            client.update_credits(member)
            buy_tokens.send(sender=order.__class__, instance=order)
        elif ipn_obj.item_name and ipn_obj.item_number:
            item=Item.objects.get(id=ipn_obj.item_number)
            invoice = AuctionInvoice.objects.get(uid=ipn_obj.invoice)
            auction = invoice.auction
            auction.status = 'paid'
            auction.save()
            invoice.status = 'paid'
            invoice.save()
            
        logger.debug("Finish payment....")
        
payment_was_successful.connect(payment_callback)
'''
Signals and handlers for the aplication.
'''

from django.dispatch.dispatcher import receiver, Signal
import uuid
import threading
import logging

logger = logging.getLogger('django')

from django.template.loader import render_to_string
from django.core.mail import send_mass_mail
from open_facebook.exceptions import PermissionException
from django.conf import settings
import json

import client

auction_finished_signal = Signal(providing_args=["auction"])
precap_finished_signal = Signal(providing_args=["auction"])

task_auction_start = Signal(providing_args=["auction"])
task_auction_pause = Signal(providing_args=["auction"])


@receiver(auction_finished_signal)
def send_win_email(sender, **kwargs):
    try:
        client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: auction_finished_signal'}),
                                   '/topic/main/')
        logger.debug("Sending mail")
        auction = kwargs['auction']
        user = auction.winner

        if user and auction.bid_type == 'bid':
            print "sending email"

            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags

            subject = render_to_string('bidding/auction_won_subject.txt',
                                       {'user': user,
                                        'item': auction.item}).replace('\n', '')
            from_email = settings.DEFAULT_FROM_EMAIL
            to = user.email

            html_content = render_to_string('bidding/mail_winner.html',
                                            {'user': user,
                                             'auction': auction,
                                             'site': settings.SITE_NAME,
                                             'images_site': settings.IMAGES_SITE})
            text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

            # create the email, and attach the HTML version as well.
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    except Exception:
        logging.info('signal.send_win_email', exc_info=True)
        raise


@receiver(auction_finished_signal)
def make_auction_invoice(sender, **kwargs):
    auction = kwargs['auction']
    client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: auction_finished_signal'}),
                               '/topic/main/')

    if auction.winner:

        from bidding.models import AuctionInvoice

        invoice = AuctionInvoice()
        invoice.auction = auction
        invoice.member = auction.winner.get_profile()
        invoice.uid = uuid.uuid4()
        invoice.save()

        #winnner for fun earns retail price in tokens!
        if auction.bid_type == 'token':
            mem = auction.winner.get_profile()
            mem.tokens_left += int(auction.item.retail_price)
            mem.save()

            client.callReverse(mem.facebook_id, 'reloadTokens')


#@receiver(precap_finished_signal)
def send_start_email(sender, **kwargs):
    client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: precap_finished_signal'}),
                               '/topic/main/')
    auction = kwargs['auction']

    user_mails = auction.bidder_mails()

    subject = render_to_string('bidding/auction_start_subject.txt',
                               {'item': auction.item}).replace('\n', '')

    message = render_to_string('bidding/auction_start_email.txt',
                               {'auction': auction,
                                'site': settings.SITE_NAME})

    data_tuples = []
    for mail in user_mails:
        data_tuples.append((subject, message, settings.DEFAULT_FROM_EMAIL, [mail]))

    send_mass_mail(data_tuples)


@receiver(auction_finished_signal)
def post_win_story(sender, **kwargs):
    auction = kwargs['auction']
    logger.debug("story")
    logger.debug("Auction: %s" % auction)
    print auction.winner
    if auction.winner:
        member = auction.winner.get_profile()
        if auction.bid_type == 'token':
            args = {'product':'http://ibid.sytes.net/fb_test_item',} #'{url}.format(url=auction.item.url)
            try:
                member.post_win_story(**args)
            except PermissionException:
                print "User forbid story post"
            except:
                raise

def send_in_thread(signal, **kwargs):
    """ 
    Sends the given signal in a different thread, so it doesn't delay further
    actions.
    """
    ## to disable thread uncomment this
    #signal.send(**kwargs)

    th = threading.Thread(target=signal.send, kwargs=kwargs)
    th.start()


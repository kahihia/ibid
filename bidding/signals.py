'''
Signals and handlers for the aplication.
'''

import json
import logging
import threading
import uuid

from open_facebook import OpenFacebook, FacebookAuthorization 
from django.conf import settings
from django.core.mail import send_mass_mail
from django.dispatch.dispatcher import receiver, Signal
from django.template.loader import render_to_string

import client

auction_threshold_signal = Signal(providing_args=["number"])
auction_started_signal = Signal()
auction_finished_signal = Signal()
precap_finishing_signal = Signal()
precap_finished_signal = Signal()
task_auction_start = Signal()
task_auction_pause = Signal()

logger = logging.getLogger('django')


@receiver(auction_finished_signal)
def send_win_email(sender, **kwargs):
    try:
        client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: auction_finished_signal'}),
                                   '/topic/main/')
        logger.debug("Sending mail")
        auction = sender
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
    auction = sender
    client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: auction_finished_signal'}),
                               '/topic/main/')

    if auction.winner:

        from bidding.models import AuctionInvoice

        invoice = AuctionInvoice()
        invoice.auction = auction
        invoice.member = auction.winner
        invoice.uid = uuid.uuid4()
        invoice.save()

        #winnner for fun earns retail price in tokens!
        if auction.bid_type == 'token':
            mem = auction.winner
            mem.tokens_left += int(auction.item.retail_price)
            mem.save()

            client.callReverse(mem.facebook_id, 'reloadTokens')


#@receiver(precap_finished_signal)
def send_start_email(sender, **kwargs):
    client.send_pubnub_message(json.dumps({'method': 'log', 'params': 'SERVER: precap_finished_signal'}),
                               '/topic/main/')
    auction = sender

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
    

@receiver(auction_started_signal)
def notify_bidders_started(sender, **kwargs):
    kwargs['auction'] = sender
    kwargs['signal'] = 'auction_started'
    th = threading.Thread(target=notify_bidders_thread, kwargs=kwargs)
    th.start()


@receiver(precap_finishing_signal)
def notify_bidders_starting(sender, **kwargs):
    kwargs['auction'] = sender
    kwargs['signal'] = 'precap_finishing'
    th = threading.Thread(target=notify_bidders_thread, kwargs=kwargs)
    th.start()


def notify_bidders_thread(**kwargs):
    auction = kwargs['auction']
    text = ''
    if kwargs['signal'] == 'auction_started':
        text = u'The auction for a {item} has started. Hurry and go win it!.'.format(item=auction.item.name)
    if kwargs['signal'] == 'precap_finishing':
        text = u'The auction for a {item} is about to start. Go play for it!.'.format(item=auction.item.name)
    for member in auction.bidders.all():
        of = OpenFacebook(member.access_token)
        args = {'template': text,
            'access_token': FacebookAuthorization.get_app_access_token()}
        destination = '{facebook_id}/notifications'.format(facebook_id=member.facebook_id)
        response = of.set(destination, **args)


def send_in_thread(signal, **kwargs):
    """ 
    Sends the given signal in a different thread, so it doesn't delay further
    actions.
    """
    logger.debug(kwargs)
    th = threading.Thread(target=signal.send, kwargs=kwargs)
    th.start()


@receiver(auction_finished_signal)
def send_app_notification(sender, **kwargs):
    from apps.main.models import Notification
    auction = sender
    for bid in auction.bid_set.filter(used_amount=0):
        tmp = {}
        tmp['itemName'] = auction.item.name
        tmp['itemImage'] = auction.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auction.winner.first_name,
                         'displayName': auction.winner.display_name(),
                         'facebookId': auction.winner.facebook_id}
        tmp['won_price'] = str(auction.won_price)
        Notification.objects.create(recipient=bid.bidder, sender=None, notification_type='FinishedAuction', message=json.dumps(tmp))

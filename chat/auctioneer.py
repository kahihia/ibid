'''
Functions to handle auctioneer messages on auction chat.
'''
from django.utils.safestring import mark_safe
from chat.views import do_send_message
from chat.models import AuctioneerPhrase, Message
from bidding import client

def create_auctioneer_message(auction, message):
    message = Message.objects.create(text=message, auction=auction)

    text = message.format_message()

    tmp = {}

    tmp['auctioneerMessages'] = [{'text':text,
        'date': message.get_time()
        }]
    tmp['id'] = auction.id

    result = {'method':'receiveAuctioneerMessage', 'data': tmp}
    return (result, '/topic/main/%s' % auction.id)


def send_auctioneer_message(auction, message):
    db_msg = Message.objects.create(text=message, auction=auction)
    client.do_send_auctioneer_message(auction, db_msg)

def member_joined_message(auction, member):
    text = AuctioneerPhrase.objects.get(key='joined').text
    message = text.format(user=member.display_name(), facebook_id=member.facebook_id)
    return create_auctioneer_message(auction, mark_safe(message))

def member_claim_message(auction, member):
    if auction.bid_type == 'bid':
        text = AuctioneerPhrase.objects.get(key='claimITEMS').text
    else:
        text = AuctioneerPhrase.objects.get(key='claimTOKENS').text
    message = text.format(user=member.display_name(), price=auction.price(), facebook_id=member.facebook_id)
    return create_auctioneer_message(auction, mark_safe(message))

def member_left_message(auction, member):
    text = AuctioneerPhrase.objects.get(key='left').text
    message = text.format(user=member.display_name(), facebook_id=member.facebook_id)
    return create_auctioneer_message(auction, mark_safe(message))

def precap_finished_message(auction):
    text = AuctioneerPhrase.objects.get(key='precap').text
    send_auctioneer_message(auction, text)

def threshold_message(auction, number):
    if number == 1:
        perc = 25
        secs = auction.threshold1
    elif number == 2:
        perc = 50
        secs = auction.threshold2
    elif number == 3:
        perc = 75
        secs = auction.threshold3
    
    text = AuctioneerPhrase.objects.get(key='threshold').text
    message = text.format(perc=perc, secs=secs)
    send_auctioneer_message(auction, message)

def auction_finished_message(auction):
    if auction.winner:
        member = auction.winner
        if auction.bid_type == "bid":
            text = AuctioneerPhrase.objects.get(key='finishITEMS').text
        elif auction.bid_type == "token":
            text = AuctioneerPhrase.objects.get(key='finishTOKENS').text
        message = text.format(user=member.display_name(), price=auction.price(), facebook_id=member.facebook_id, item=auction.item)
        send_auctioneer_message(auction, message)


def initialize_phrases():
    """ Creates the default auctioneer phrases on the database. """
    
    phrase, created = AuctioneerPhrase.objects.get_or_create(key='joined')
    if created:
        phrase.text = "{user} has joined the auction!"
        phrase.description = "Displayed when a user joins an auction.\
                             {user} is replaced by the username."
        phrase.save()

    phrase, created = AuctioneerPhrase.objects.get_or_create(key='left')
    if created:
        phrase.text = "{user} has left the auction."
        phrase.description = "Displayed when a user leaves an auction.\
                             {user} is replaced by the username."
        phrase.save()
    
    phrase, created = AuctioneerPhrase.objects.get_or_create(key='precap')
    if created:
        phrase.text = "Precap finished. Auction will start in a few seconds."
        phrase.description = "Displayed when precap finishes."
        phrase.save()
    
    phrase, created = AuctioneerPhrase.objects.get_or_create(key='threshold')
    if created:
        phrase.text = "{perc}% of bids placed. I'm lowering the time frame\
                        to {secs} seconds. Auction will resume in 15\
                        seconds."
        phrase.description = "Displayed when a completion threshold is\
                                reached. {perc} is replaced by the completion\
                                percentage and {secs} by the new time\
                                frame."
        phrase.save()
    
    phrase, created = AuctioneerPhrase.objects.get_or_create(key='finish')
    if created:
        phrase.text = "{user} won the auction!"
        phrase.description = "Displayed when the auction finishes.\
                            {user} is replaced by the username."
        phrase.save()

#initialize_phrases()
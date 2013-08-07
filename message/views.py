# -*- coding: utf-8 -*-
# Create your views here.

from datetime import datetime

from django.http import HttpResponse

from bidding.models import Auction
from chat.models import Message

import message.value_objects as vo
import message.value_objects_factory as vo_factory


def message_listener(request, method):
    """api calls go through this method"""
    #TODO: put event listener here
    result = globals()[method](request)
    print result
    #TODO: put event dispatcher here
    return HttpResponse(result.toJson(), content_type="application/json")


def initialize(request):
    member = request.user.get_profile()

    eventList = vo.EventList()

    event = vo.Event()
    event['event'] = vo.Event.EVENT.MAIN__LOAD_USER_DETAILS
    event['data'] = vo_factory.create_voLoggedInUser(member)
    event['sender'] = vo.Event.SENDER.SERVER
    event['receiver'] = vo.Event.RECEIVER.CLIENT_FB + str(member.facebook_id)
    event['transport'] = vo.Event.TRANSPORT.REQUEST
    event['timestamp'] = datetime.now()
    event['id'] = None

    eventList.append(event)

    my_auctions = Auction.objects.filter(is_active=True).exclude(status__in=('waiting_payment', 'paid')).order_by(
        '-status').filter(bidders=member)
    other_auctions = Auction.objects.filter(is_active=True).exclude(
        status__in=('waiting_payment', 'paid', 'waiting', 'processing', 'pause')).order_by('-status').exclude(
        bidders=member)
    finished_auctions = Auction.objects.filter(is_active=True, status__in=(
        'waiting_payment', 'paid', 'waiting', 'processing', 'pause')).filter(winner__isnull=False).order_by('-won_date')

    allAuctions = []
    allAuctions.extend(my_auctions)
    allAuctions.extend(other_auctions.filter(bid_type='bid')[:12])
    allAuctions.extend(other_auctions.filter(bid_type='token')[:12])
    allAuctions.extend(finished_auctions.filter(bid_type='bid')[:12])
    allAuctions.extend(finished_auctions.filter(bid_type='token')[:12])

    auctions = []

    for auct in allAuctions:
        auction = vo_factory.create_voAction(auct, member)

        if auction['mine'] and auction['status'] == 'processing':
            for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:20]:
                w = vo_factory.create_voAuctioneerMessage(mm)
                auction['auctioneerMessages'].append(w)

            for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:20]:
                w = vo_factory.create_voMessage(mm)
                auction['chatMessages'].insert(0, w)

        auctions.append(auction)

    event = vo.Event()
    event['event'] = vo.Event.EVENT.MAIN__LOAD_AUCTIONS
    event['data'] = auctions
    event['sender'] = vo.Event.SENDER.SERVER
    event['receiver'] = vo.Event.RECEIVER.CLIENT_FB + str(member.facebook_id)
    event['transport'] = vo.Event.TRANSPORT.REQUEST
    event['timestamp'] = datetime.now()
    event['id'] = None

    eventList.append(event)

    #send main:friendInvitationAccepted event
    memberEvents = member.getSession('event', None)
    if memberEvents:
        event = vo.Event()
        event['event'] = vo.Event.EVENT.MAIN__FRIEND_INVITATION_ACCEPTED
        event['data'] = memberEvents[0]
        event['sender'] = vo.Event.SENDER.SERVER
        event['receiver'] = vo.Event.RECEIVER.CLIENT_FB + str(member.facebook_id)
        event['transport'] = vo.Event.TRANSPORT.REQUEST
        event['timestamp'] = datetime.now()
        event['id'] = None

        eventList.append(event)

    return eventList






def static(request):
    """api calls go through this method"""

    sta = """
[{"sender": "server", "timestamp": 1375904088, "id": null, "receiver": "client-fb-100001640641493", "data": {"name": "Daniel Nuske", "tokens": 56395, "credits": 9255, "pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493}, "event": "main:loadUserDetails", "transport": "request"}, {"sender": "server", "timestamp": 1375904089, "id": null, "receiver": "client-fb-100001640641493", "data": [{"completion": 0, "status": "precap", "winner": "", "timeleft": null, "itemImage": "http://localhost:8000/media/cache/de/72/de7204830bca001150c5e8fdfca617f6.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "600.00", "bids": 0, "mine": false, "placed": 0, "bidPrice": 5, "bidders": 0, "itemName": "Ferragamo Woman's Watch", "id": 202, "auctioneerMessages": []}, {"completion": 0, "status": "precap", "winner": "", "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": false, "placed": 0, "bidPrice": 5, "bidders": 0, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 203, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 201, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/de/72/de7204830bca001150c5e8fdfca617f6.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "600.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "Ferragamo Woman's Watch", "id": 137, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 136, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100006430451468/picture", "link": "https://www.facebook.com/profile.php?id=100006430451468", "id": 100006430451468, "name": "James Chaistein"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": false, "placed": 0, "bidPrice": 100, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 124, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/f4/e4/f4e4f0a8db6bc42ba809e46a06b2c2ee.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "600.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 4, "bidders": 1, "itemName": "Sennheiser RS 220 Headphone Black", "id": 127, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 9, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 126, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 56, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/de/72/de7204830bca001150c5e8fdfca617f6.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "600.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "Ferragamo Woman's Watch", "id": 55, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 54, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/22/bf/22bff14fa19cc25a6c293ab8acd5704e.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "Apple iPhone 5 64Gb Unlocked (White", "id": 42, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 41, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/be/e7/bee70778cc29998128fa45d504db32fa.jpg", "bidType": "credit", "bidNumber": 0, "chatMessages": [], "retailPrice": "929.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPad Retina 64Gb Wi-Fi + 4G Black (Factory Unlocked)", "id": 38, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/22/bf/22bff14fa19cc25a6c293ab8acd5704e.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 10, "bidders": 1, "itemName": "Apple iPhone 5 64Gb Unlocked (White", "id": 215, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/22/bf/22bff14fa19cc25a6c293ab8acd5704e.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 10, "bidders": 1, "itemName": "Apple iPhone 5 64Gb Unlocked (White", "id": 213, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 212, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 211, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 210, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 209, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 208, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 207, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 206, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 205, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 204, "auctioneerMessages": []}, {"completion": 0, "status": "waiting_payment", "winner": {"pictureUrl": "https://graph.facebook.com/100001640641493/picture", "link": "http://www.facebook.com/dnuske", "id": 100001640641493, "name": "Daniel Nuske"}, "timeleft": null, "itemImage": "http://localhost:8000/media/cache/c2/b1/c2b1467d6afb0754cb465b56ad147240.jpg", "bidType": "token", "bidNumber": 0, "chatMessages": [], "retailPrice": "919.00", "bids": 0, "mine": true, "placed": 0, "bidPrice": 5, "bidders": 1, "itemName": "iPhone 5 64Gb Black", "id": 200, "auctioneerMessages": []}], "event": "main:loadAuctions", "transport": "request"}, {"sender": "server", "timestamp": 1375904089, "id": null, "receiver": "client-fb-100001640641493", "data": {"prize": 1001, "users": [{"pictureUrl": "https://graph.facebook.com/None/picture", "link": "http://facebook.com/123123123", "id": 12312342354, "name": "pepe"}]}, "event": "main:friendInvitationAccepted", "transport": "request"}]"""

    return HttpResponse(sta, content_type="application/json")



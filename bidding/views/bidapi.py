import json

from django.http import HttpResponse
from django.conf import settings

from bidding.delegate import GlobalAuctionDelegate
from bidding.delegate import oldclient_delayStop
from bidding.models import Auction, AuctionFixture


def api(request, method ):
    return API[method](request)


def finish(request):
    auctionId = int(request.GET.get('auctionId'))
    bidNumber = int(request.GET.get('bidNumber'))
    time = float(request.GET.get('time', 0))

    auction = GlobalAuctionDelegate(Auction.objects.get(id=auctionId))

    print "====stop====",auction

    print auction.status, bidNumber, auction.used_bids()/auction.minimum_precap
    if auction.status == 'processing' and bidNumber == auction.used_bids()/auction.minimum_precap:
        # finish
        auction.finish()

        # run auction fixtures #
        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='token')) == 0:
            aifx = AuctionFixture.objects.filter(bid_type='token')
            if len(aifx):
                rt = aifx[0].make_auctions()
                print "rt = aifx[0].make_auctions()", rt

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='bid')) == 0:
            aifx = AuctionFixture.objects.filter(bid_type='bid')
            if len(aifx):
                rt = aifx[0].make_auctions()
                print "rt = aifx[0].make_auctions()", rt

    return HttpResponse(json.dumps({'everyThingIsFine':True}))


def start(request):
    auctionId = int(request.GET.get('auctionId'))
    bidNumber = int(request.GET.get('bidNumber'))
    time = float(request.GET.get('time', 0))
    kwargs = {'auctionId': auctionId,
              'bidNumber': bidNumber,
              'time': time}

    auction = GlobalAuctionDelegate(Auction.objects.get(id=auctionId))
    print "====start====",auction

    print auction.status
    if auction.status == 'waiting':
        # start
        print "<<< auction start"
        auction.start()
        oldclient_delayStop(auctionId, 0, auction.auction.bidding_time)
    elif auction.status == 'pause':
        # resume
        print "<<< auction resume"
        auction.resume()
        oldclient_delayStop(auctionId, auction.getBidNumber(), auction.auction.bidding_time)
        
    return HttpResponse(json.dumps({'everyThingIsFine':True}))


API = {
    'finish': finish,
    'start': start,
}


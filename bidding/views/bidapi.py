from django.http import HttpResponse
from django.conf import settings
import json

from bidding import client
from bidding.delegate import GlobalAuctionDelegate
from bidding.models import Auction, AuctionFixture

import bid_client

def api(request, method ):
    return API[method](request)

def finish(request):
    auctionId = int(request.GET.get('auctionId'))
    bidNumber = int(request.GET.get('bidNumber'))
    time = float(request.GET.get('time', 0))

    auction = GlobalAuctionDelegate(Auction.objects.get(id=auctionId))

    print "====stop====",auction

    #if status == processing #and bidNumber is the last
    print auction.status, bidNumber, auction.used_bids()/auction.minimum_precap
    if auction.status == 'processing' and bidNumber == auction.used_bids()/auction.minimum_precap:

        #########
        # finish #
        #########

        #logger.info(' - - %s finish', self.id)
        auction.finish()

        ########################
        # run auction fixtures #
        ########################

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='token')) == 0:
            #run first token fixture
            aifx = AuctionFixture.objects.filter(bid_type='token')
            if len(aifx):
                rt = aifx[0].make_auctions()
                print "rt = aifx[0].make_auctions()", rt

        if len(Auction.objects.filter(is_active=True).filter(status='precap').filter(bid_type='bid')) == 0:
            #run first bids fixture
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

        #########
        # start #
        #########

        #logger.info(' - - %s liveAuction start, timeleft:%s', str(self.id), str(timeLeft))
        print "<<< auction start"
        auction.start()
        # --- delay the LiveAuction stop call to be called if no one bid ---
        ##self.delayMethod(self.callStop, time=timeLeft, auctionId=self.id)
        bid_client.delayStop(auctionId, 0, auction.auction.bidding_time)

    elif auction.status == 'pause':
        ##########
        # resume #
        ##########

        #logger.info(' - - %s resume', self.id)
        #logger.info(' - - %s auction current status %s', self.id, str(self.auction.auction.status))
        print "<<< auction resume"
        auction.resume()

        ##self.delayMethod(self.callStop, time=self.auction.auction.bidding_time, auctionId=self.id)
        bid_client.delayStop(auctionId, auction.getBidNumber(), auction.auction.bidding_time)
        
    return HttpResponse(json.dumps({'everyThingIsFine':True}))

API = {
    'finish': finish,
    'start': start,
}


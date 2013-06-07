
from bidding.models import Auction
from bidding.delegate import PrecapAuctionDelegate,WaitingAuctionDelegate,RunningAuctionDelegate,PausedAuctinoDelegate,StateAuctionDelegate,StateAuctionDelegate

class GlobalAuctionDelegate(Auction): #, PrecapAuctionDelegate, WaitingAuctionDelegate, RunningAuctionDelegate, PausedAuctinoDelegate):

    def __getattr__(self, name):
        """ Tries to forward non resolved calls to the delegate objects. """
        logger.debug("Name: %s" % name)
        for sd in all_delegates:
            if hasattr(sd, name):
                return getattr(sd, name)

            if hasattr(super(Auction, self), '__getattr__'):
                return super(Auction, self).__getattr__(name)

        raise AttributeError

all_delegates = [PrecapAuctionDelegate,
                 WaitingAuctionDelegate,
                 RunningAuctionDelegate,
                 PausedAuctinoDelegate,
                 StateAuctionDelegate,
                 StateAuctionDelegate]


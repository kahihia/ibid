__author__ = 'dnuske'

import bidding.value_objects as vo


def create_voAction(auction, member):

    if auction.status == "precap":
        tmp = {}
        tmp['id'] = auct.id
        tmp['completion'] = auct.completion()
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_token_available.append(tmp)
    if auction.status == "pause":
        tmp = {}

        tmp['id'] = auct.id
        if hasattr(auct, 'completion'):
            tmp['completion'] = auct.completion()
        else:
            tmp['completion'] = 0
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:10]:

            w = vo.AuctioneerMessage(date = mm.get_time(),
                                 text = mm.format_message(),
                                 auctionId = auct.id)

            auction['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:10]:
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': auct.id
            }
            tmp['chatMessages'].insert(0, w)

        auctions_token_my.append(tmp)
    if auction.status == "waiting":
        tmp = {}

        tmp['id'] = auct.id
        if hasattr(auct, 'completion'):
            tmp['completion'] = auct.completion()
        else:
            tmp['completion'] = 0
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:10]:

            w = vo.AuctioneerMessage(date = mm.get_time(),
                                 text = mm.format_message(),
                                 auctionId = auct.id)

            auction['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:10]:
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': auct.id
            }
            tmp['chatMessages'].insert(0, w)

        auctions_token_my.append(tmp)
    if auction.status == "processing":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = auction.getBidNumber(),
                               bids = auction.auction_bids_left(auction),
                               placed = member.auction_bids_left(auction),
                               mine = False,
                               bidPrice = auction.minimum_precap,
                               bidType = {'tokens': 'token', 'bids': 'credit'}[auction.bid_type])

        if hasattr(auction, 'completion'):
            vo_auction['completion'] = auction.completion()
        else:
            vo_auction['completion'] = 0

        if auction.status == 'processing':
            vo_auction['timeleft'] = auction.get_time_left()
        else:
            vo_auction['timeleft'] = None

        return vo_auction





        tmp = {}

        tmp['id'] = auct.id
        if hasattr(auct, 'completion'):
            tmp['completion'] = auct.completion()
        else:
            tmp['completion'] = 0
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['timeleft'] = auct.get_time_left() if auct.status == 'processing' else None
        tmp['bidNumber'] = auct.used_bids() / auct.minimum_precap if auct.status == 'processing' else 0
        tmp['placed'] = member.auction_bids_left(auct)
        tmp['bids'] = member.auction_bids_left(auct)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['bidders'] = auct.bidders.count()

        tmp['auctioneerMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=True).order_by('-created')[:10]:

            w = vo.AuctioneerMessage(date = mm.get_time(),
                                 text = mm.format_message(),
                                 auctionId = auct.id)

            auction['auctioneerMessages'].append(w)

        tmp['chatMessages'] = []
        for mm in Message.objects.filter(auction=auct).filter(_user__isnull=False).order_by('-created')[:10]:
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': auct.id
            }
            tmp['chatMessages'].insert(0, w)

        auctions_token_my.append(tmp)
    if auction.status == "waiting_payment":
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name,
                         'displayName': auct.winner.get_profile().display_name(),
                         'facebookId': auct.winner.get_profile().facebook_id}
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_token_finished.append(tmp)
    if auction.status == "paid":
        tmp = {}
        tmp['id'] = auct.id
        tmp['status'] = auct.status
        tmp['bidPrice'] = auct.minimum_precap
        tmp['bidType'] = 'token'
        tmp['itemName'] = auct.item.name
        tmp['bidNumber'] = 0
        tmp['bids'] = 0
        tmp['placed'] = 0
        tmp['retailPrice'] = str(auct.item.retail_price)
        tmp['itemImage'] = auct.item.get_thumbnail(size="107x72")
        tmp['winner'] = {'firstName': auct.winner.get_profile().user.first_name,
                         'displayName': auct.winner.get_profile().display_name(),
                         'facebookId': auct.winner.get_profile().facebook_id}
        tmp['auctioneerMessages'] = []
        tmp['chatMessages'] = []

        auctions_token_finished.append(tmp)






__author__ = 'dnuske'

import message.value_objects as vo


def create_voAction(auction, member):

    if auction.status == "precap":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = 0,
                               bids = 0,
                               placed = 0,
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left(),
                               winner = '',
                               completion = auction.completion())

        return vo_auction

    if auction.status == "pause":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = auction.getBidNumber(),
                               bids = auction.auction_bids_left(auction),
                               placed = member.auction_bids_left(auction),
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left())

        if hasattr(auction, 'completion'):
            vo_auction['completion'] = auction.completion()
        else:
            vo_auction['completion'] = 0

        return vo_auction
    if auction.status == "waiting":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = auction.getBidNumber(),
                               bids = auction.auction_bids_left(auction),
                               placed = member.auction_bids_left(auction),
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left())

        if hasattr(auction, 'completion'):
            vo_auction['completion'] = auction.completion()
        else:
            vo_auction['completion'] = 0

        return vo_auction
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
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left())

        if hasattr(auction, 'completion'):
            vo_auction['completion'] = auction.completion()
        else:
            vo_auction['completion'] = 0

        return vo_auction
    if auction.status == "waiting_payment":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = 0,
                               bids = 0,
                               placed = 0,
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left(),
                               winner = create_voUser(auction.winner.get_profile()),
                               completion = 0)

        return vo_auction

    if auction.status == "paid":
        vo_auction = vo.Auction(status = auction.status,
                               itemImage = auction.item.get_thumbnail(size="107x72"),
                               retailPrice = str(auction.item.retail_price),
                               bidders = auction.bidders.count(),
                               itemName = auction.item.name,
                               id = auction.id,
                               bidNumber = 0,
                               bids = 0,
                               placed = 0,
                               mine = member in auction.bidders.all(),
                               bidPrice = auction.minimum_precap,
                               bidType = {'token': 'token', 'bid': 'credit'}[auction.bid_type],
                               timeleft = auction.get_time_left(),
                               winner = create_voUser(auction.winner.get_profile()),
                               completion = 0)

        return vo_auction


def create_voAuctioneerMessage(message):
    return vo.AuctioneerMessage(date = message.get_time(),
                                text = message.format_message(),
                                auctionId = message.auction.id)


def create_voLoggedInUser(member):
    return vo.LoggedInUser(member.facebook_id,
                           member.display_name(),
                           member.facebook_profile_url,
                           member.display_picture(),
                           member.bids_left,
                           member.tokens_left)


def create_voUser(member):
    return vo.User(member.facebook_id,
                   member.display_name(),
                   member.facebook_profile_url,
                   member.display_picture(),
                   )

def create_voFriendInvitationAccepted(prize, invited):
    return vo.FriendInvitationAccepted(
        prize,
        create_voUser(invited)
    )

var PRECAP = 0;
var WAITING = 1;
var PROCESSING = 2;
var PAUSE = 3;
var WAITING_PAYMENT = 4;
var PAID = 5;

var statuses = {
    'precap': 0,
    'waiting': 1,
    'processing': 2,
    'pause': 2,
    'waiting_payment': 4,
    'paid': 5
};

//keep record of the game state to send when reporting an error
var gameState = {pubnubMessages:[]};

/*var auctionPrecapData = {
 itemName: 'Mackbook Pro 15" i7',
 retailPrice: '300.00',
 completion: 12,
 placed: 15,
 bids: 15,
 itemImage: '',
 bidders: 43
 };*/

/*function AuctionPrecapCtrl($scope) {
 $scope.name = 'World';
 $scope.itemName = 'Mackbook Pro 15" i7';
 $scope.retailPrice = '300.00';
 $scope.completion = 12;
 $scope.placed = 15;
 $scope.bids = 15;
 $scope.itemImage = '';
 $scope.bidders = 43;
 };*/


function AuctionsPanelController($scope, $rootScope, $http, $timeout) {

    //$scope.messages = [];
    //$scope.message = {'method': '', data: {}};
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;
    $scope.showItemDetails = false;

    $rootScope.playFor = $scope.AUCTION_TYPE_TOKENS;


    $scope.initializeAuctions = function () {
        $http
            .get('/api/getAuctionsInitialization/')
            .success(function (auctionsCollection) {
                console.log('Got auctions', auctionsCollection);
                $scope.auctionList = auctionsCollection;
                _.forEach(auctionsCollection, function (auctionsSub) {
                    _.forEach(auctionsSub, function (auctionsSub2) {
                        _.forEach(auctionsSub2, $scope.initializeAuction);
                    });
                });
            });
    };

    $scope.initializeAuction = function (auction) {
        // Add values to control the user interface aspect.
        auction.interface = {
            bidEnabled: true,
            isWinning: false,
            addBidEnabled: $scope.isUserAbleToAddBidToAuction(auction),
            remBidEnabled: true,
            joinAuctionEnabled: true,
            can_bid: true
        };
        // Initialize default values.
        if (_.isUndefined(auction.chatMessage)) {
            auction.chatMessage = '';
        }
        // If user is participating in auction, subscribe to channel.
        if ($scope.isAuctionMine(auction)) {
            auction.interface.joinAuctionEnabled = false;
            $scope.subscribeToAuctionChannel(auction);
        }
        // If auction has a timeleft, it already begun, so counter
        // must be started and last bidder should be checked in case
        // it's current user to disable bid button (maybe the user
        // reloaded the page?).
        if (!_.isUndefined(auction.timeleft)) {
            $scope.startCounter(auction.id);
        }
        // If auction's last bidder is current user, disable bid
        // button.
        if (auction.lastBidder && auction.lastBidder.facebookId === $rootScope.user.facebookId) {
            auction.interface.bidEnabled = false;
            auction.interface.isWinning = true;
        }
    };

    $scope.isAuctionMine = function (auction) {
        return _.contains($scope.auctionList[$scope.AUCTION_TYPE_TOKENS]['mine'], auction) || _.contains($scope.auctionList[$scope.AUCTION_TYPE_CREDITS]['mine'], auction);
    };

    $scope.isUserAbleToAddBidToAuction = function (auction) {
        switch (auction.bidType) {
        case $scope.AUCTION_TYPE_TOKENS:
            return $rootScope.user.tokens >= auction.bidPrice;
        case $scope.AUCTION_TYPE_CREDITS:
            return $rootScope.user.credits >= auction.bidPrice;
        }
    };

    //switch between TOKENS and ITEMS
    $scope.playForTokens = function () {
        $rootScope.playFor = $scope.AUCTION_TYPE_TOKENS;
    }

    $scope.playForItems = function () {
        $rootScope.playFor = $scope.AUCTION_TYPE_CREDITS;
        $scope.$emit('showItemAuctions');
    }

    $scope.subscribeToAuctionChannel = function (auction) {
        // Subscribe to auction actions channel.
        $scope.subscribeToChannel({
            channel: $scope.channel + auction.id,
            message: function (messages) {
                _.forEach(messages, function (message) {
                    console.log('PubNub channel %s message (%s)', $scope.channel + auction.id, getCurrentDateTime(), message);
                    gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                    $scope.$apply(function () {
                        switch (message.method) {
                        case 'receiveAuctioneerMessage':
                            auction.auctioneerMessages.unshift(message.data.auctioneerMessages[0]);
                            break;
                        case 'someoneClaimed':
                            if (message.data.lastClaimer !== $rootScope.user.displayName) {
                                auction.interface.isWinning = false;
                                if (auction.interface.can_bid) {
                                    auction.interface.bidEnabled = true;
                                }
                            }
                            else if (message.data.lastClaimer === $rootScope.user.displayName) {
                                auction.interface.isWinning = true;
                            }
                            auction.timeleft = message.data.timeleft;
                            auction.bidNumber = message.data.bidNumber;
                            $scope.startCounter(auction.id);
                            break;
                        }
                    });
                });
            }
        });
        // Subscribe to auction chat channel.
        $scope.subscribeToChannel({
            channel: '/topic/chat/' + auction.id,
            message: function (messages) {
                _.forEach(messages, function (message) {
                    console.log('PubNub channel %s message (%s)', '/topic/chat/' + auction.id, getCurrentDateTime(), message);
                    gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                    $scope.$apply(function () {
                        var auction;
                        // Try to get auction data once without errors.
                        // TODO: In the near future, messages will be
                        // standarized so hopefully we don't need this.
                        try {
                            auction = $scope.getLocalAuctionById(message.data.id);
                        }
                        catch (e) {}
                        auction.chatMessages.push(message.data);
                    });
                });
            }
        });
    };

    $scope.addAuctionAvailable = function () {
        this.auctionsAvailable.push({type: 'email', value: 'yourname@example.org'});
    };

    $scope.startBidding = function (auction) {
        // If auction is not in precapitalization status or user has
        // already joined, do nothing.
        if (auction.status !== 'precap' || ! auction.interface.joinAuctionEnabled) {
            return;
        }
        auction.interface.joinAuctionEnabled = false;
        //tutorial
        if(tutorialActive == true && tutorialAuctionId == auction.id){
            $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent2');}, 2500);
        }
        // Post to server that user wants to start bidding on this
        // auction.
        $http
            .post('/api/v1/auction/'+auction.id+'/add_bids/')
            .success(function (data) {
                // User can't bid on this auction.
                if (!data.success) {
                    if (data.motive === 'NO_ENOUGH_CREDITS') {
                        // TODO: Show tip using a service.
                        $rootScope.$emit('openGetCreditsPopover');
                    }
                    else if (data.motive === 'NO_ENOUGH_TOKENS') {
                        // TODO: Show tip using a service.
                        console.log('not enough tokens');
                    }
                    auction.interface.joinAuctionEnabled = true;
                    return;
                }
                // Update auction with data received from the
                // server. Use _.extend() to avoid removing Angular's
                // $$hashKey property.
                _.extend(auction, data.auction);
                // Move auction to mine.
                $scope.moveAuction(auction, 'available', 'mine');
                // Reload user data to refresh tokens/credits.
                $rootScope.$emit('reloadUserDataEvent');
                $scope.$emit('joinAuction');
            });
    };

    /**
     * Adds bids to an auction.
     *
     * @param {object} auction Auction to add bids to.
     */
    $scope.addBids = function (auction) {
        // If auction status is not precapitalization, do nothing.
        if (auction.status !== 'precap') {
            return;
        }
        // If add bid button is not enabled, do nothing.
        if (! auction.interface.addBidEnabled) {
            return;
        }
        // If user is not able to add bids, emit failure event and
        // return.
        if (! $scope.isUserAbleToAddBidToAuction(auction)) {
            var event = auction.bidType === $scope.AUCTION_TYPE_TOKENS ? 'addTokensBidFailed' : 'addCreditsBidFailed';
            console.log('addBids() -- isUserAbleToAddBidToAuction: false -- emit event: %s', event);
            $scope.$emit(event);
            return;
        }
        // Disable add/rem bid buttons.
        auction.interface.addBidEnabled = false;
        auction.interface.remBidEnabled = false;
        // Post to the API the intention to add bids to auction.
        $http
            .post('/api/v1/auction/'+auction.id+'/add_bids/')
            .success(function (rdata, status) {
                console.log('addBids()', rdata);
                // If the bid can't be added, do corresponding action.
                if (rdata.success === false) {
                    console.log('addBids() -- server responded: failed -- motive: %s', rdata.motive);
                    if (rdata.motive === 'NO_ENOUGH_CREDITS'){
                        // Emit event for failure.
                        $scope.$emit('addCreditsBidFailed');
                    }
                    else if (rdata.motive === 'NO_ENOUGH_TOKENS'){
                        // Emit event for failure.
                        $scope.$emit('addTokensBidFailed');
                    }else if (rdata.motive === 'AUCTION_MAX_TOKENS_REACHED') {
                        console.log('Amount commited exceeds maximum for user in an auction');
                        // Re-enable add/rem bid buttons.
                        auction.interface.addBidEnabled = false;
                        auction.interface.remBidEnabled = true;
                    }
                    return;
                }
                // Re-enable add/rem bid buttons.
                auction.interface.addBidEnabled = true;
                auction.interface.remBidEnabled = true;
                // Bid could be added, so changes are reflected in UI.
                auction.bids = auction.placed = rdata.data.placed;
                // Emit event to reload user data.
                $rootScope.$emit('reloadUserDataEvent');
            });
    };

    /**
     * Removes bids from an auction.
     *
     * @param {object} auction Auction to remove bids from.
     */
    $scope.remBids = function (auction) {
        // If auction status is not precapitalization, or i didn't
        // placed any bid, do nothing.
        if (auction.status !== 'precap' || ! auction.placed) {
            return;
        }
        // If remove bid button is not enabled, do nothing.
        if (! auction.interface.remBidEnabled) {
            return;
        }
        // Disable add/rem bid buttons.
        auction.interface.addBidEnabled = false;
        auction.interface.remBidEnabled = false;
        // Post to the API the intention to remove bids from auction.
        $http
            .post('/api/remBids/', {id: auction.id})
            .success(function (response) {
                if (!response.success) {
                    return;
                }
                // Re-enable add/rem bid buttons.
                auction.interface.addBidEnabled = true;
                auction.interface.remBidEnabled = true;
                // If server tells that it was my last bid, i have to
                // quit bidding on this auction.
                if (response.data && response.data['do'] === 'close') {
                    $scope.stopBidding(auction);
                    return;
                }
                // Update auction with placed bids.
                // TODO: Unify `auction.placed` with `auction.bids`.
                auction.placed = response.data.placed;
                auction.bids = response.data.placed;
                // Emit event to reload user data.
                $rootScope.$emit('reloadUserDataEvent');
            });
    };

    /**
     * Stops bidding on an auction.
     *
     * @param {object} auction Auction to stop bidding on.
     */
    $scope.stopBidding = function (auction) {
        // Unsubscribe from auction channel.
        $scope.unsubscribeFromChannel($scope.channel + auction.id);
        // Reload user data to update tokens/credits.
        $rootScope.$emit('reloadUserDataEvent');
        // Move auction to available auctions.
        $scope.moveAuction(auction, 'mine', 'available');
    };


    /**
     * Bid on auction.
     *
     * @param {object} auction
     */
    $scope.claim = function (auction) {
        if (auction.status !== 'processing') {
            console.error('Bid on non-processing auction');
        }
        if (auction.interface.bidEnabled === true && auction.bids > 0) {
            console.log("Bid on auction %s", auction.id);
            auction.interface.bidEnabled = false;
            $http
                .post('/api/claim/', {'id': auction.id, 'bidNumber': auction.bidNumber})
                .success(function (response) {
                    if (!response.success) {
                        console.log('Bid on auction %s failed', auction.id);
                        // Bid failed, reset bid button.
                        auction.interface.bidEnabled = true;
                        return;
                    }
                    console.log('Bid on auction %s succeeded', auction.id);
                    auction.bids -= auction.bidPrice;
                    $rootScope.$emit('reloadUserDataEvent');
                    auction.interface.can_bid = ((response.placed_amount - response.used_amount) > 0);
                });
        }
    };

    $scope.auctionTimeouts = {};

    $scope.startCounter = function (auctionId) {
        var auction = $scope.getLocalAuctionById(auctionId);
        if(typeof auction.auctionTimeouts != 'undefined'){
            $timeout.cancel(auction.auctionTimeouts);
        }
        auction.onTimeout = function(){
            if (typeof auction.timeleft === 'number') {
                if (auction.timeleft > 1) {
                    auction.timeleft = auction.timeleft - 1;
                    auction.auctionTimeouts = $timeout(auction.onTimeout, 1000);
                }
            }
        };

        auction.auctionTimeouts = $timeout(auction.onTimeout, 1000);
    };




    //publish a chat message
    $scope.sendChatMessage = function (index) {
        auction = $scope.auctionList[$rootScope.playFor].mine[index];
        if (auction.chatMessage != ''){
            console.log('sendChatMessage', auction.chatMessage);
            $http.post('/api/sendMessage/', {id: auction.id, user: $rootScope.user, text:auction.chatMessage}).
                success(function (rdata, status) {
                    console.log("chatmessage on auction " + auction.id);
                });

            auction.chatMessage = '';
        }

    }

    /**
     * Method to move an auction from mine to finished.
     *
     * @param {object} auction Auction to move.
     */
    $scope.closeAuction = function (auction) {
        $scope.moveAuction(auction, 'mine', 'finished');
    };

    //getLocalAuctionsAll
    $scope.getLocalAuctionAll = function () {
        var auctions = [];
        auctions = [].concat(auctions, $scope.auctionList[$scope.AUCTION_TYPE_TOKENS]['mine'], $scope.auctionList[$scope.AUCTION_TYPE_TOKENS]['available'], $scope.auctionList[$scope.AUCTION_TYPE_TOKENS]['finished']);
        auctions = [].concat(auctions, $scope.auctionList[$scope.AUCTION_TYPE_CREDITS]['mine'], $scope.auctionList[$scope.AUCTION_TYPE_CREDITS]['available'], $scope.auctionList[$scope.AUCTION_TYPE_CREDITS]['finished']);
        return auctions;
    }

    //getLocalAuctionById
    $scope.getLocalAuctionById = function (_id) {
        var auctions = $scope.getLocalAuctionAll();
        for (idx in auctions) {
            if (auctions[idx].id == _id) {
                return auctions[idx]
            }
        }
    }

    $scope.getLocalAuctionByIndex = function (toksorcreds, mineoravailableorfinished, index) {
        return $scope.auctionList[toksorcreds][mineoravailableorfinished][index];
    }

    /**
     * Move auction from one place to another inside of the auctionList
     * array (ie, from "mine" to "available").
     *
     * @param {object} auction The auction to move.
     * @param {string} from    The source location (ie, "mine").
     * @param {string} to      The destination location (ie, "available").
     */
    $scope.moveAuction = function (auction, from, to) {
        var sourceAuctions = $scope.auctionList[auction.bidType][from];
        sourceAuctions.splice(_.indexOf(sourceAuctions, auction), 1);
        $scope.auctionList[auction.bidType][to].push(auction);
        // Call initializeAuction() again to reset auction data.
        $scope.initializeAuction(auction);
    };

    $scope.subscribeToChannel = function (options) {
        _.defaults(options, {
            connect: function () {
                console.log('PubNub channel %s connected', options.channel);
            },
            message: function (messages) {
                _.forEach(messages, function (message) {
                    console.log('PubNub channel %s message (%s)', options.channel, getCurrentDateTime(), message);
                });
            },
            reconnect: function () {
                console.log('PubNub channel %s reconnected', options.channel);
                $scope.$apply(function () {
                    $scope.realtimeStatus = 'Connected';
                });
            },
            disconnect: function () {
                console.log('PubNub channel %s disconnected', options.channel);
                $scope.$apply(function () {
                    $scope.realtimeStatus = 'Disconnected';
                });
            },
            error: function (data) {
                console.log('PubNub channel %s network error', options.channel, data);
            }
        });
        return PUBNUB.subscribe(options);
    };

    $scope.unsubscribeFromChannel = function (channel) {
        return PUBNUB.unsubscribe({
            channel: channel
        });
    };


    // Connect to main channel.
    $scope.subscribeToChannel({
        channel: $scope.channel,
        connect: function () {
            console.log('PubNub channel %s connected', $scope.channel);
            hideOverlay();
        },
        message: function (messages) {
            _.forEach(messages, function (message) {
                console.log('PubNub channel %s message (%s)', $scope.channel, getCurrentDateTime(), message);
                gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                $scope.$apply(function () {
                    switch (message.method) {
                    case 'appendAuction':
                        $scope.auctionList[message.data.bidType].available.push(message.data);
                        $scope.initializeAuction(message.data);
                        break;
                    case 'updateAuction':
                        var auction = $scope.getLocalAuctionById(message.data.id);
                        // If received auction data has a lower status
                        // than current auction status, do nothing.
                        if (!_.isUndefined(message.data.status) && statuses[message.data.status] < statuses[auction.status]) {
                            console.log('updateAuction -- Received status is lower than current auction status. Doing nothing.');
                            return;
                        }
                        // Update auction with received data.
                        // Use _.extend() to avoid removing Angular's
                        // $$hashKey property.
                        _.extend(auction, message.data);
                        // Based on received status, do corresponding
                        // action.
                        switch (auction.status) {
                        case 'processing':
                            // Auction started, start counter.
                            $scope.startCounter(auction.id);
                            // Tutorial.
                            if (tutorialActive && tutorialAuctionId === auction.id) {
                                $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent3');}, 500);
                            }
                            // Emit event after minimal timeout to be
                            // sure bid button is already displayed.
                            // This is specially for the interactive
                            // tour. Consider moving the timeout onto
                            // it?
                            $timeout(function () {
                                $scope.$emit('auctionStart');
                            },50);
                            break;
                        case 'waiting_payment':
                            $scope.$emit('auction:finished', auction, $scope.auctionList);
                            // Tutorial.
                            if (tutorialActive && tutorialAuctionId === auction.id) {
                                $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent5');}, 500);
                            }
                            break;
                        }
                        break;
                    }
                });
            });
        }
    });

    //to close a popup, this may be in base_header.js but the html has to follow
    $scope.closeGetCredits = function() {
        $rootScope.$emit('closeGetCreditsPopover');
    };

    $scope.loadItemDetails = function(auction) {
        $http
            .get('/api/v1/auction/'+auction.id)
            .success(function (auctionInfo) {
                //var details = "<div class='item-image'><img src='"+auctionInfo['item']['itemImage']+"'></div><p>"+auctionInfo['item']['description']+"</p>";
                
                var details ='<div class="item"><img src="'+auctionInfo['item']['itemImage']+'"><p class="winner"><span class="item-name">'+auctionInfo['item']['name']+'</span></p></div><p class="info text-small-w">'+auctionInfo['item']['description']+'</p>';             
                angular.element('#item-details').html(details);
                $scope.showItemDetails = true;
                showOverlay();
        });
    };
    
    $scope.hideItemDetails = function() {
        $scope.showItemDetails = false;
        hideOverlay();    
    };
    
    $scope.initializeAuctions();
};


function aaaaaa(p) {
    if (Object.prototype.toString.call(p) === '[object Array]') {
        return true;
    } else {
        return false;
    }
}
function isDict(p) {
    if (Object.prototype.toString.call(p) === '[object Object]') {
        return true;
    } else {
        return false;
    }
}

jQuery(function(){
    showOverlay();
})

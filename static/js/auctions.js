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

//var auctionList = {"tokens": {"available": [{"completion": 0, "status": "precap", "tokens_or_bids_in_it": 0, "bid_type": "token", "itemImage": "http://apps.facebook.com/interactivebids/media/cache/7a/a4/7aa4be77b318539465c35622b532be4d.jpg", "title": "WII", "minimum_precap": 56, "img_url": "http://apps.facebook.com/interactivebids/media/cache/7a/a4/7aa4be77b318539465c35622b532be4d.jpg", "retailPrice": "249.99", "bids": 9999, "bidders_count": 0, "placed": 9999, "itemName": "WII", "bids_left": 0, "bidders": 0, "retail_price": "249.99", "chat_enabled": false, "id": 6}, {"completion":0,"status":"precap","tokens_or_bids_in_it":0,"bid_type":"token","itemImage":"http://apps.facebook.com/interactivebids/media/cache/7a/a4/7aa4be77b318539465c35622b532be4d.jpg","title":"WII","minimum_precap":56,"img_url":"http://apps.facebook.com/interactivebids/media/cache/7a/a4/7aa4be77b318539465c35622b532be4d.jpg","retailPrice":"249.99","bids":9999,"bidders_count":0,"placed":9999,"itemName":"WII","bids_left":0,"bidders":0,"retail_price":"249.99","chat_enabled":false,"id":6}], "finished": [], "mine": []}, "credits": {"available": [], "finished": [], "mine": []}}

function AuctionsPanelController($scope, $rootScope, $http, $timeout) {

    //$scope.messages = [];
    //$scope.message = {'method': '', data: {}};
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;

    $rootScope.playFor = 'TOKENS';

    $scope.$on('reloadAuctionsData', function () {
        $http.post('/api/getAuctionsInitialization/').
            success(function (data, status) {
                console.log('Got auctions', data);
                $scope.auctionList = data;
                $scope.initializeAuctions();
                $scope.profileFotoLink = $rootScope.user.profileFotoLink;
            });
    })

    $scope.initializeAuctions = function () {
        var auctions = $scope.getLocalAuctionAll();
        for (idx in auctions) {
            $scope.initializeAuction(auctions[idx]);
        }
    }

    $scope.initializeAuction = function (auction) {
        // Add values to control the user interface aspect.
        auction.interface = {
            bidEnabled: true,
            addBidEnabled: $scope.isAddBidsEnabled(),
            remBidEnabled: true
        };
        // Initialize default values.
        if (_.isUndefined(auction.chatMessage)) {
            auction.chatMessage = '';
        }
        else {
            alert('initializeAuction() -- auction.chatmessage is defined!');
        }
        if ($scope.isAuctionMine(auction)) {
            $scope.subscribeToAuctionChannel(auction);
        }
        // If auction has a timeleft, it already begun, so counter
        // must be started.
        if (!_.isUndefined(auction.timeleft)) {
            $scope.startCounter(auction.id);
        }
    };

    $scope.isAuctionMine = function (auction) {
        return _.contains($scope.auctionList['TOKENS']['mine'], auction) || _.contains($scope.auctionList['ITEMS']['mine'], auction);
    };

    $scope.isAddBidsEnabled = function () {
        return $rootScope.user.tokens > 0;
    }

    //switch between TOKENS and ITEMS
    $scope.playForTokens = function () {
        $rootScope.playFor = 'TOKENS';
    }

    $scope.playForItems = function () {
        $rootScope.playFor = 'ITEMS';
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
                        var auction;
                        // Try to get auction data once without errors.
                        // In the near future, messages will be
                        // standarized so hopefully we don't need this.
                        try {
                            auction = $scope.getLocalAuctionById(message.data.id);
                        }
                        catch (e) {}
                        switch (message.method) {
                        case 'receiveAuctioneerMessage':
                            auction.auctioneerMessages.unshift(message.data.auctioneerMessages[0]);
                            break;
                        case 'someoneClaimed':
                            if (message.data.lastClaimer !== $rootScope.user.displayName) {
                                auction.interface.bidEnabled = true;
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
                    console.log('PubNub channel %s message (%s)', '/topic/chat' + auction.id, getCurrentDateTime(), message);
                    gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                    $scope.$apply(function () {
                        var auction;
                        // Try to get auction data once without errors.
                        try {
                            auction = $scope.getLocalAuctionById(message.data.id);
                        }
                        catch (e) {}
                        auction.chatMessages.push(message.data);
                        var scrollHeight = jQuery(jQuery(".chat-list", jQuery(jQuery("input[value='"+auction.id+"']", '#user-auctions')[0]).next()[0])[0])[0].scrollHeight;
                        setTimeout(function(){jQuery(jQuery(".chat-list", jQuery(jQuery("input[value='"+auction.id+"']", '#user-auctions')[0]).next()[0])[0]).scrollTop(scrollHeight)} ,200);
                    });
                });
            }
        });
    };

    $scope.addAuctionAvailable = function () {
        this.auctionsAvailable.push({type: 'email', value: 'yourname@example.org'});
    };

    $scope.startBiding = function (auction) {
        //if($scope.auctionsAvailable[index].status <> "precap"){console.log('ERROR: startBiding - not precap')};

        // If auction is not in precapitalization status, do nothing.
        if (auction.status !== 'precap') {
            return;
        }

        console.log("Joined auction", auction);

        //tutorial
        if(tutorialActive == true && tutorialAuctionId == auction.id){
            $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent2');}, 2500);
        }
        $http
            .post('/api/startBidding/', {'id': auction.id})
            .success(function (rdata, status) {
                $rootScope.$emit('reloadUserDataEvent');
                //remove auction from available and load it into mine
                delete auction; //auctionList.tokens.available.splice(index);
                $scope.$emit('reloadAuctionsData');
            });
        // Subscribe to auction's message channel.
        $scope.subscribeToAuctionChannel(auction);
    };

    //status: precap
    $scope.addBids = function (auction) {
        if (auction.status != "precap") {
            console.log('ERROR: addBids - not precap');
        }

        //if user has tokens/credits
        if ($scope.isAddBidsEnabled()) {

            auction.placed += 5;
            auction.bids += 5;

            console.log("addBids on auction " + auction.id);
            $http.post('/api/addBids/', {'id': auction.id}).
                success(function (rdata, status) {
                    if(rdata.success == true){
                        $rootScope.$emit('reloadUserDataEvent');
                    }else{
                        console.log("no more credits/tokens");
                        auction.placed -= 5;
                        auction.bids -= 5;
                    }

                });

        }

    };

    //status: precap
    $scope.remBids = function (auction) {
        // If status is not precapitalization, can't remove bids.
        if (auction.status !== "precap") {
            return;
        }

        //if user has bids on auction
        if(auction.placed>0){
            auction.placed -= 5;
            auction.bids -= 5;

            console.log("remBids on auction " + auction.id);

            //if does not have more bids on auction leave
            if (auction.bids == 0) {
                $scope.stopBiding(auction);
            } else {
                $http.post('/api/remBids/', {'id': auction.id}).
                    success(function (rdata, status) {
                        $rootScope.$emit('reloadUserDataEvent');
                    });
            }
        }
    };

    $scope.stopBiding = function (auction) {
        //if($scope.auctionsAvailable[index].status <> "precap"){console.log('ERROR: startBiding - not precap')};

        // If status is not precapitalization, can't stop bidding.
        if (auction.status !== 'precap') {
            return;
        }

        console.log("Stopped bidding on auction", auction);

        $http
            .post('/api/stopBidding/', {'id': auction.id})
            .success(function (rdata, status) {
                // Unsubscribe from auction channel.
                $scope.unsubscribeFromChannel($scope.channel + auction.id);

                $rootScope.$emit('reloadUserDataEvent');
                //remove auction from available and load it into mine
                delete auction;
                $scope.$emit('reloadAuctionsData');
            });
    };


    //status processing
    $scope.claim = function (auction) {
        if (auction.status != "processing") {
            console.log('ERROR: claim - not processing');
        }

        if (auction.interface.bidEnabled == true && auction.bids > 0) {
            console.log("claim on auction " + auction.id)

            //auction.placed -= 5;
            auction.bids = (auction.bids-5);
            auction.interface.bidEnabled = false;

            $http.post('/api/claim/', {'id': auction.id, 'bidNumber': auction.bidNumber}).
                success(function (rdata, status) {
                    console.log('-- rdata --');
                    console.log(rdata);
                    if (rdata['result']){
                        $rootScope.$emit('reloadUserDataEvent');
                    }else{
                        //TODO: add loading state.
                        auction.bids = (auction.bids+5);
                        auction.interface.bidEnabled = true;
                    }
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

    //getLocalAuctionsAll
    $scope.getLocalAuctionAll = function () {
        var auctions = [];
        auctions = [].concat(auctions, $scope.auctionList['TOKENS']['mine'], $scope.auctionList['TOKENS']['available'], $scope.auctionList['TOKENS']['finished']);
        auctions = [].concat(auctions, $scope.auctionList['ITEMS']['mine'], $scope.auctionList['ITEMS']['available'], $scope.auctionList['ITEMS']['finished']);
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
            console.log('test messages', messages);
            _.forEach(messages, function (message) {
                console.log('message', message);
                console.log('PubNub channel %s message (%s)', $scope.channel, getCurrentDateTime(), message);
                gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                $scope.$apply(function () {
                    var auction;
                    // Try to get auction data once without errors.
                    try {
                        auction = $scope.getLocalAuctionById(message.data.id);
                    }
                    catch (e) {}
                    switch (message.method) {
                    case 'appendAuction':
                        if (message.data.playFor == 'TOKENS') {
                            $scope.auctionList['TOKENS']['available'].push(message.data);
                        }
                        else if (message.data.playFor == 'ITEMS') {
                            $scope.auctionList['ITEMS']['available'].push(message.data);
                        }
                        $scope.initializeAuction(message.data);
                        break;
                    case 'updateAuction':
                        //check if the comming status is equal or higher than the actual
                        if (typeof message.data.status == 'undefined' || statuses[message.data.status] >= statuses[auction.status]) {
                            //overwrite the auction values with the new ones
                            jQuery.extend(auction, message.data);
                            if (message.data.status === 'waiting_payment') {
                                console.log('WAITING PAYMENT!', auction.status);
                            }
                            //if this pack changes the timeleft, start da counter
                            if (message.data.status == 'processing'){
                                $scope.startCounter(auction.id);
                            }
                            if (tutorialActive == true && tutorialAuctionId == auction.id){
                                if (message.data.status == 'processing'){
                                    $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent3');}, 500);
                                }
                                if (message.data.status == 'waiting_payment'){
                                    $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent5');}, 500);
                                }
                            }
                        }
                        break;
                    }
                });
            });
        }
    });

    //firt load all auctions, when all functions are declared;
    $scope.$emit('reloadAuctionsData');

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

function getCurrentDateTime(){
    //to parse in python
    //>>> time.strptime("2013-05-25 02:04:09.2", '%Y-%m-%d %H:%M:%S.%f')

    var currentdate = new Date();
    var datetime = currentdate.getFullYear() + "-"
                    + (currentdate.getMonth()+1)  + "-"
                    + currentdate.getDate() + " "
                    + currentdate.getHours() + ":"
                    + currentdate.getMinutes() + ":"
                    + currentdate.getSeconds() + "."
                    + currentdate.getMilliseconds()
    return datetime;
}



jQuery(function(){
    showOverlay();
})

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

    $scope.messages = [];
    $scope.message = {'method': '', data: {}};
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;

    $rootScope.playFor = 'TOKENS';

    $scope.$on('reloadAuctionsData', function () {
        $http.post('/api/getAuctionsInitialization/').
            success(function (data, status) {
                $scope.auctionList = data;
                console.log('initialize auctions');
                console.log($scope.auctionList);
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
        //add values to controll the user interface aspect
        auction.interface = {'bidEnabled': true,
            'addBidEnabled': $scope.isAddBidsEnabled(),
            'remBidEnabled': true
        };
        //initialize default variable values
        if(typeof auction.auctioneerMessages == 'undefined'){
            auction.auctioneerMessages = [];
        }

    }
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




    $scope.addAuctionAvailable = function () {
        this.auctionsAvailable.push({type: 'email', value: 'yourname@example.org'});
    };

    $scope.startBiding = function (auction) {
        //if($scope.auctionsAvailable[index].status <> "precap"){console.log('ERROR: startBiding - not precap')};
        console.log("start bidding on auction " + auction.id)
        //tutorial
        if(tutorialActive == true && tutorialAuctionId == auction.id){
            $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent2');}, 2500);
        }
        $http.post('/api/startBidding/', {'id': auction.id}).
            success(function (rdata, status) {
                $rootScope.$emit('reloadUserDataEvent');
                //remove auction from available and load it into mine
                delete auction; //auctionList.tokens.available.splice(index);
                $scope.$emit('reloadAuctionsData');
            });
    };

    //status: precap
    $scope.addBids = function (auction) {
        if (auction.status != "precap") {
            console.log('ERROR: addBids - not precap');
        }

        //if user has tokens/credits
        console.log('----------');
        console.log($scope.isAddBidsEnabled());
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
        if (auction.status != "precap") {
            console.log('ERROR: remBids - not precap');
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
        console.log("stop bidding on auction " + auction.id)
        $http.post('/api/stopBidding/', {'id': auction.id}).
            success(function (rdata, status) {
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

            $http.post('/api/claim/', {'id': auction.id}).
                success(function (rdata, status) {
                    $rootScope.$emit('reloadUserDataEvent');
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
            if( typeof auction.timeleft == 'number'){
                if( auction.timeleft > 0){
                    auction.timeleft = auction.timeleft - 1;
                    auction.auctionTimeouts = $timeout(auction.onTimeout, 1000);
                }
            }
        }

        auction.auctionTimeouts = $timeout(auction.onTimeout, 1000);
    };




    //publish a chat message
    $scope.sendChatMessage = function (index) {
        console.log('sendChatMessage', $scope.message);

        thisAuction = $scope.auctionList[$rootScope.playFor].mine[index];
        //toggle the progress bar
        //$('#progress_bar').slideToggle();


        $scope.message.method = "receiveChatMessage";
        $scope.message.data.auctionId = thisAuction.id;
        $scope.message.data.user = $rootScope.user;
        PUBNUB.publish({
            channel: $scope.channel,
            message: $scope.message
        })

        //reset the message text
        console.log('sendChatMessage', $scope.message);

        $scope.message.data.text = '';

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


    //we'll leave these ones as is so that pubnub can
    //automagically trigger the events
    PUBNUB.subscribe({
        channel: $scope.channel,
        //restore    : false,

        callback: function (message) {
            console.log("pubnub message:", message);
            gameState.pubnubMessages.push([getCurrentDateTime(), message]);

            $scope.$apply(function () {
                //read the method and do
                if (message.method == 'receiveChatMessage') {
                    $scope.messages.unshift(message.data);
                } else if (message.method == 'receiveAuctioneerMessage') {
                    var auction = $scope.getLocalAuctionById(message.data.id);
                    auction.auctioneerMessages.unshift(message.data.auctioneerMessages[0]);
                } else if (message.method == 'updateAuction') {
                    var auction = $scope.getLocalAuctionById(message.data.id);
                    //check if the comming status is equal or higher than the actual
                    if (typeof message.data.status == 'undefined' || statuses[message.data.status] >= statuses[auction.status]) {
                        //overwrite the auction values with the new ones
                        jQuery.extend(auction, message.data);
                        //if this pack changes the timeleft, start da counter
                        if (message.data.status == 'processing'){
                            $scope.startCounter(auction.id);
                        }
                        if(tutorialActive == true && tutorialAuctionId == auction.id){
                            if (message.data.status == 'processing'){
                                $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent3');}, 500);
                            }
                            if (message.data.status == 'waiting_payment'){
                                $timeout(function(){jQuery('#btn-tutorial','#tooltip-help').trigger('tutorialEvent5');}, 500);
                            }
                        }

                    }
                } else if (message.method == 'appendAuction') {
                    if(message.data.playFor=='TOKENS'){
                        $scope.auctionList['TOKENS']['available'].push(message.data);
                        $scope.initializeAuction(message.data);
                    }else if(message.data.playFor=='ITEMS'){
                        $scope.auctionList['ITEMS']['available'].push(message.data);
                        $scope.initializeAuction(message.data);
                    }
                } else if (message.method == 'someoneClaimed') {
                    var auction = $scope.getLocalAuctionById(message.data.id);
                    //console.log(classes['bidEnabled'][auction.interface.bidEnabled]);

                    if (message.data.lastClaimer != $rootScope.user.displayName) {
                        var auction = $scope.getLocalAuctionById(message.data.id);
                        auction.interface.bidEnabled = true;
                    }else{console.log('------------AAAARRRRRLGGGGGHHHH-----------')}
                    auction.timeleft = message.data.timeleft;
                    $scope.startCounter(auction.id);
                }
            });
        },

        disconnect: function () {
            console.log('pubnub NOTconnected')
            $scope.$apply(function () {
                $scope.realtimeStatus = 'Disconnected';
            });
        },

        reconnect: function () {
            $scope.$apply(function () {
                $scope.realtimeStatus = 'Connected';
            });
        },

        connect: function () {
            console.log('pubnub connected');
            hideOverlay();
            /**$scope.$apply(function(){
                $scope.realtimeStatus = 'Connected';
                //hide the progress bar
                $('#progress_bar').slideToggle();
                //load the message history from PubNub
                $scope.history();
            });*/

        }
    })

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

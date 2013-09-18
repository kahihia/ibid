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

// var userDetailsData = {
//     displayName: '',
//     tokens: 0,
//     profileFotoLink: '',
//     credits: 0,
//     profileLink: ''
// };

function userDetailsCtrl($scope, $rootScope, $http, notification) {

    //initialization
    $rootScope.app = {};
    $rootScope.app.tokenValueInCredits = 0;
    $rootScope.app.applink = 'https://apps.facebook.com/ibidgames';
    $rootScope.app.apppicture = "https://apps.facebook.ibidgames.com/static/images/400x400-Fblogo.png";

    $rootScope.user = {};
    $rootScope.user.displayName = '';
    $rootScope.user.profileFotoLink = '';
    $rootScope.user.profileLink = '';
    $rootScope.user.tokens = 0;
    $rootScope.user.credits = 0;
    $rootScope.user.username = '';
    $rootScope.user.first_name = '';
    $rootScope.user.last_name = '';
    $rootScope.user.facebook_id = '';
    $rootScope.user.email = '';

    $rootScope.convertTokens = {}
    //TODO: get this value on "app initialization" event
    $rootScope.convertTokens.tokenValueInCredits = 0;

    $rootScope.convertTokens.tokens = 0;
    $rootScope.convertTokens.credits = 0;

    //define channel
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;
    
    $scope.initialize = function (mixpanel_token) {
        //initialize analythics.js with mixpanel
        analytics.initialize({
            'Mixpanel' : {
                token  : mixpanel_token,
                people : true
            },
        });
        // API request get user details
        $http.post('/api/getUserDetails/').success(function (data) {
            // identify users
            analytics.identify(data.user.username, {
                email: data.user.email,
                name : data.user.first_name,
                last_name : data.user.last_name,
                fb_id : data.user.facebookId
            });
            $rootScope.user = data.user;
            $rootScope.convertTokens.tokenValueInCredits = data.app.tokenValueInCredits;
        });
    };
    
    $rootScope.$on('reloadUserDataEvent', function () {
        $http
            .post('/api/getUserDetails/')
            .success(function (data) {
                $scope.user.tokens = data.user.tokens;
                $scope.user.credits = data.user.credits;

                $rootScope.convertTokens.credits = parseInt($rootScope.user.tokens*$rootScope.convertTokens.tokenValueInCredits);
                $rootScope.convertTokens.tokens = $rootScope.convertTokens.credits/$rootScope.convertTokens.tokenValueInCredits;
            });
    });
    $rootScope.$on('openGetCreditsPopover', function () {
        // showOverlay();
        // setTimeout(function () {
        //     jQuery('.buy-bids-popup').show();
        //     TweenLite.fromTo('.buy-bids-popup', 1, {left: '50px'},{left: '150x', ease: Back.easeOut});
        // }, 300);
        $scope.showBuyCreditsModal = true;

        //what to show on convert tokens
        $rootScope.convertTokens.credits = parseInt($rootScope.user.tokens*$rootScope.convertTokens.tokenValueInCredits);
        $rootScope.convertTokens.tokens = $rootScope.convertTokens.credits/$rootScope.convertTokens.tokenValueInCredits;

    });
    $rootScope.$on('closeGetCreditsPopover', function () {
//        hideOverlay();
//        TweenLite.to('.buy-bids-popup', 1, {left: '-800px', onComplete: function () {
//            jQuery('.buy-bids-popup').hide();
//        }})
        $scope.showBuyCreditsModal = false;
    });
    $rootScope.$on('auction:finished', function (event, auction) {
        // If current user won, show win modal.
        if (auction.winner.facebookId !== $scope.user.facebookId) {
            return;
        }
        $scope.wonAuction = auction;
        $scope.showWonTokensDialog = (auction.bidType === $scope.AUCTION_TYPE_TOKENS);
        $scope.showWonItemDialog = (auction.bidType === $scope.AUCTION_TYPE_CREDITS);
        // If playing for tokens, update user tokens.
        if (auction.bidType !== $scope.AUCTION_TYPE_TOKENS) {
            return;
        }
        $rootScope.user.tokens += Number(auction.retailPrice);
    });



    $scope.closeWonAuctionDialog = function () {
        //request for perm if does not have it
        $scope.requestPermisionPublishActions();

        $scope.showWonTokensDialog = null;
        $scope.showWonItemDialog = null;
    };

    $scope.closeWonAuctionDialogAndPlayForItems = function () {
        $scope.closeWonAuctionDialog();
        $rootScope.playFor = $scope.AUCTION_TYPE_CREDITS;
    };

    /**
     * Shows notification after users invited.
     *
     * @param {object} event Event object.
     */
    var userInvitedHandler = function (event) {
        $scope.$apply(function () {
            notification.show('The invitations have been sent! Thank you!');
        });
    };
    $scope.$on('user:invited', userInvitedHandler);

    $scope.showJoinedFriendsDialog = function (event, data) {
        $scope.joinedFriendsData = data;
    };

    $rootScope.$on('user:friendJoined', $scope.showJoinedFriendsDialog);

    $scope.hideJoinedFriendsDialog = function (showInviteMoreFriends) {
        $scope.joinedFriendsData = null;
        if (showInviteMoreFriends) {
            $scope.sendRequestViaMultiFriendSelector();
        }
    };

    $scope.convertChips = function() {
        if ( $rootScope.convertTokens.credits > 0){
            $http
                .post('/api/convertTokens/')
                .success(
                function (data, status) {
                    $rootScope.$emit('reloadUserDataEvent');

                });
        }
    };

    $scope.shareOnTimeline = function () {
        //this is not longer used, because works weird.
        FB.ui({
            method: 'feed',
            link: $rootScope.app.applink,
            picture: $rootScope.app.apppicture

            //link: 'http://localhost:8000/canvasapp/'
        });
    };

    $scope.sendRequestViaMultiFriendSelector = function() {
        FB.ui({method: 'apprequests',
            message: 'Come join me to play and win amazing deals at iBidGames!'
        }, sendRequestViaMultiFriendSelectorCallback);
    };

    var sendRequestViaMultiFriendSelectorCallback = function (data) {
        if (data) {
            // Store invitations sent.
            $http.post('/api/inviteRequest/', {invited: data.to});
            $scope.$emit('user:invited');
        }
    };

    $scope.openGetCredits = function() {
        $rootScope.$emit('openGetCreditsPopover');
    };

    $scope.closeGetCredits = function() {
        $rootScope.$emit('closeGetCreditsPopover');
    };

    $scope.buy_bids = function(member,package_id,site_name) {
        // calling the API ...
        
        analytics.track('buy bids');
        var obj = {
            method: 'pay',
            action: 'purchaseitem',
            product: site_name+'bid_package/'+package_id,
        };
        
        $scope.subscribeToPaymentChannel(member)
        FB.ui(obj, getCredits_callback);
    };

    var getCredits_callback = function(data) {};

    $scope.subscribeToPaymentChannel = function(member) {
        $scope.subscribeToChannel({
            channel: $scope.channel + member,
            message: function(messages) {
                _.forEach(messages, function(message) {
                    console.log('PubNub channel %s message (%s)', $scope.channel + member, getCurrentDateTime(), message);
                    gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                    $scope.$apply(function () {
                        jQuery('.credits').text("CREDITS: " + message.data.credits)
                        $scope.unsubscribeFromChannel($scope.channel + member)
                    });
                });
            }
        });
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
        console.log('PubNub channel %s disconnected' , channel);
        return PUBNUB.unsubscribe({
            channel: channel
        });
    };

    $scope.fb_check_like= function() {
        $http.post('/fb_check_like/').success(
            function(data){
                if (data['like']){
                    jQuery('.button.like').addClass('disabled');
                    jQuery('.button.like').addClass('liked');
                    jQuery('.button.like').removeClass('like');
                }else{
                }});
    };

    $scope.fb_like= function() {

        $scope.requestPermisionPublishActions();

        $http
        .post('/fb_like/')
        .success(
            function (data) {
                switch (data['info']) {
                    case 'FIRST_LIKE':
                        /*
                         * In this case the user receives tokens because is the first like.
                         * data['gift'] says the amount of tokens gifted.
                         */
                        jQuery('.button.like').addClass('disabled');
                        jQuery('.button.like').addClass('liked');
                        jQuery('.button.like').removeClass('like');
                        jQuery('.tokens').text('TOKENS: ' + data['tokens']);
                        break;
                    case 'NOT_FIRST_LIKE':
                        /*
                         * In this case the user is liking but not for the first time.
                         * For example when the user stops liking in facebook and likes again.
                         * The user is not getting the tokens.
                         */
                        jQuery('.button.like').addClass('disabled');
                        jQuery('.button.like').addClass('liked');
                        jQuery('.button.like').removeClass('like');
                        break;
                    case 'ALREADY_LIKE':
                        /*
                         * This is a case that occurs when the user already likes and facebook returns
                         * a error code 3501
                         */
                        break;
                }
            }
        );

    };
    $scope.requestPermisionPublishActions = function () {
        FB.login(function (response) {

                //TODO: call api method to send the wall post
                var events = []
                if(response.authResponse){
                    events.push(new EventMessage(EventMessage.EVENT.BIDDING__UPDATE_ACCESS_TOKEN, {accessToken: response.authResponse.accessToken}, EventMessage.SENDER.CLIENT_FB, EventMessage.RECEIVER.SERVER, EventMessage.TRANSPORT.REQUEST, getCurrentDateTime(), null));
                }
                events.push(new EventMessage(EventMessage.EVENT.BIDDING__SEND_STORED_WALL_POSTS, {}, EventMessage.SENDER.CLIENT_FB, EventMessage.RECEIVER.SERVER, EventMessage.TRANSPORT.REQUEST, getCurrentDateTime(), null));

                // begin dispatcher
                console.log({events: angular.toJson(events)});
                $http
                    .get('/action/', {params: {events: angular.toJson(events)}})
                    .then(function (response) {
                        //listener - TRANSPORT request
                        _.forEach(response.data, function (message) {
                            $rootScope.$broadcast(message.event, message.data);
                        });
                    });
                // end dispatcher

        }, {scope: 'publish_actions'});
    };

    $scope.uvTabPosition=function () {
        FB.Canvas.getPageInfo(function(pageInfo){
            var num1 = parseInt(pageInfo.scrollTop);
            var num2 = parseInt(pageInfo.clientHeight);
            $('#uvTab').animate({top: ((num2/2)+num1) }, 0);
            setTimeout($scope.uvTabPosition, 100);
        });
    };

};


jQuery(function () {
    jQuery('.buy-bids-popup').hide();
})

var underlay = '.underlay';
var popupClass = '.popup';
var popupOuter = '.popup-outer';


function closePopupLike() {
    hideOverlay();
    TweenLite.to('.like-popup', 1, {left: '-800px', onComplete: function () {
        jQuery('.like-popup').hide()
    }})
}


function buy_bids(url, package_id) {
    var order_info = -1;

    jQuery.post(url, {'package_id': package_id},
        function (data) {
            if (data.order_info != undefined) {
                if (data.order_info >= 0) {

                    // calling the API ...
                    var obj = {
                        method: 'pay',
                        order_info: data.order_info,
                        purchase_type: 'item',
                        dev_purchase_params: {
                            'oscif': true
                        }
                    };
                    console.log(obj);

                    FB.ui(obj, getCredits_callback);
                }
            }
        }, 'json');
}

var getCredits_callback = function (data) {
    if (data['order_id']) {
        refresh_user_bids();
        return true;
    } else {
        // handle errors here
        return false;
    }
};

var ovarlayCount = 0;
function showOverlay(){
    ovarlayCount+=1;
    if(ovarlayCount>0){
        jQuery('#overlay').show();
        TweenLite.to('#overlay', 0.6, {opacity:1});
    }
}
function hideOverlay(){
    ovarlayCount-=1;
    if(ovarlayCount==0){
        TweenLite.to('#overlay', 0.6, {opacity:0, onComplete:function(){jQuery('#overlay').hide()}});
    }
}


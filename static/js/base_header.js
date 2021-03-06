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

    $scope.tokenAuctionsWon = []
    $scope.creditAuctionsWon = []
    
    //define channel
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;

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

    $rootScope.$on('auction:finished', function (event,auction,auctionList) {
        // If current user won, show win modal.
        if (auction.winner.id !== $scope.user.id) {
            show_token_lost_dialog  = false;
            show_item_lost_dialog  = false;
            if (auction.bidType == "bid") {
                list = auctionList[$scope.AUCTION_TYPE_CREDITS]['mine'];
                for (i =0; i < list.length; i++){
                    if (list[i].id == auction.id) {
                        show_item_lost_dialog = true;
                    }
                }
            }
            if (auction.bidType == "token") {
                list = auctionList[$scope.AUCTION_TYPE_TOKENS]['mine'];
                for (var i =0; i < list.length; i=i+1){
                    if (list[i].id == auction.id) {
                        show_token_lost_dialog = true;
                    }
                }
            }
            $scope.lostAuction = auction;
            $scope.showLostTokensDialog = show_token_lost_dialog;
            $scope.showLostItemDialog = show_item_lost_dialog;
            if (show_token_lost_dialog) {
                showOverlay();
            }
        } else {
            $scope.wonAuction = auction;
            $scope.requestPermisionPublishActions('STORY');
            $scope.showWonTokensDialog = (auction.bidType === $scope.AUCTION_TYPE_TOKENS);
            $scope.showWonItemDialog = (auction.bidType === $scope.AUCTION_TYPE_CREDITS);
            // If playing for tokens, update user tokens.
            if (auction.bidType === $scope.AUCTION_TYPE_TOKENS) {
                $rootScope.user.tokens += Number(auction.retailPrice);
            }
            showOverlay();
        }
        if (auction.bidType === $scope.AUCTION_TYPE_TOKENS) {
               $scope.tokenAuctionsWon.push(auction);
           }else {
               $scope.creditAuctionsWon.push(auction);
           };
        return;
    });

     $rootScope.subscribeToPaymentChannel = function(member) {
        $scope.subscribeToChannel({
            channel: $scope.channel + member,
            message: function(messages) {
                _.forEach(messages, function(message) {
                    console.log('PubNub channel %s message (%s)', $scope.channel + member, getCurrentDateTime(), message);
                    gameState.pubnubMessages.push([getCurrentDateTime(), message]);
                    $scope.$apply(function () {
                        try {
                            jQuery('.credits').text("CREDITS: " + message.data.credits);
                        }catch (e){
                            jQuery('.tokens').text("TOKENS: " + message.data.tokens);
                        }
                    });
                });
            }
        });
    };

    $rootScope.subscribeToChannel = function (options) {
        _.defaults(options, {
            connect: function () {
                console.log('PubNub channel %s connected', options.channel);
                console.log($rootScope.user);
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

    $rootScope.unsubscribeFromChannel = function (channel) {
        console.log('PubNub channel %s disconnected' , channel);
        return PUBNUB.unsubscribe({
            channel: channel
        });
    };
    
    $scope.closeWonTokenAuctionDialog = function () {
        $scope.tokenAuctionsWon = [];
        //request for perm if does not have it
        $scope.showWonTokensDialog = null;
        hideOverlay();
    };
    
    $scope.closeWonCreditAuctionDialog = function () {
        $scope.creditAuctionsWon = [];
        //request for perm if does not have it
        $scope.showWonItemDialog = null;
        hideOverlay();
    };

    $scope.closeWonAuctionDialogAndPlayForItems = function () {
        $scope.closeWonTokenAuctionDialog();
        $rootScope.playFor = $scope.AUCTION_TYPE_CREDITS;
    };

    $scope.closeLostAuctionDialog = function () {
        //request for perm if does not have it
        $scope.showLostTokensDialog = null;
        $scope.showLostItemDialog = null;
        hideOverlay();
    };

    $scope.closeLostAuctionDialogAndPlayForItems = function () {
        $scope.closeLostAuctionDialog();
        $rootScope.playFor = $scope.AUCTION_TYPE_CREDITS;
        hideOverlay();
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
            $rootScope.sendRequestViaMultiFriendSelector();
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
        FB.ui({
            method: 'feed',
            link: $rootScope.app.applink,
            picture: $rootScope.app.apppicture
        });
    };

    $rootScope.sendRequestViaMultiFriendSelector = function() {
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
        showOverlay();
        $rootScope.$emit('openGetCreditsPopover');
    };

    $scope.closeGetCredits = function() {
        $rootScope.$emit('closeGetCreditsPopover');
        hideOverlay();
    };

    $scope.buy_bids = function(member,package_id,$event) {
        // calling the API ...
        $(".purchase_popup .joyride-tip-guide").css('top', ($(window).height()/2)-90);
        $(".purchase_popup").removeClass("hidden");
        dom_elem=$event.target
        $(dom_elem).find('form').submit();
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
    

    $scope.fb_story= function() {
        var events = [];
        events.push(new EventMessage(EventMessage.EVENT.BIDDING__SEND_WALL_POSTS, {auction:$scope.wonAuction}, EventMessage.SENDER.CLIENT_FB, EventMessage.RECEIVER.SERVER, EventMessage.TRANSPORT.REQUEST, getCurrentDateTime(), null));
        $http
            .get('/action/', {params: {events: angular.toJson(events)}})
            .then(function (response) {
                console.log(response);
            });
    };


    $scope.fb_like= function() {

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
    $scope.requestPermisionPublishActions = function (method) {
        FB.login(function (response) {
            var events = []
            events.push(new EventMessage(EventMessage.EVENT.BIDDING__UPDATE_ACCESS_TOKEN, {accessToken: response.authResponse.accessToken}, EventMessage.SENDER.CLIENT_FB, EventMessage.RECEIVER.SERVER, EventMessage.TRANSPORT.REQUEST, getCurrentDateTime(), null));
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

            if (response.authResponse) {
                switch (method) {

                    case 'LIKE':
                        $scope.fb_like();
                        break;

                    case 'STORY':
                        $scope.fb_story();
                        break;
                }
            }
        }, {scope: 'publish_actions'});
    };

    $rootScope.$on('InitializeUvTabPosition',  function (event, data) {
        $scope.uvTabPosition();
    });

    $scope.uvTabPosition = function () {
        try {
            FB.Canvas.getPageInfo(function (pageInfo) {
                var scrollTop = parseInt(pageInfo.scrollTop);
                var clientHeight = parseInt(pageInfo.clientHeight);

                angular.element('#uvTab').animate({top: (clientHeight / 2) + scrollTop}, 0);
                angular.element('#uvw-dialog-uv-1').animate({top: (clientHeight / 2) + scrollTop}, 0);
                angular.element('#uvTab').css({zIndex: '1000'});

                
                
                if (!!angular.element('.modal:visible').length) {
                    var $tip = angular.element('.modal:visible');
                    $tip.animate({top: (clientHeight / 2) - ($tip.height() / 2)}, 0);
                    FB.Canvas.scrollTo(0, 0);
                }
                
                // If tour is showing a modal tip, fix it's position
                // on canvas.
                if (!!angular.element('.joyride-modal-bg:visible').length) {
                    var $tip = angular.element('.joyride-tip-guide:visible');
                    $tip.animate({top: (clientHeight / 2) - ($tip.height() / 2)}, 0);
                    FB.Canvas.scrollTo(0, 0);
                }
            });
        }
        finally {
            setTimeout($scope.uvTabPosition, 100);
        }
    };

    $scope.messageJsonParse = function (message) {
        console.log(angular.fromJson(message['message']));
        message['message'] = angular.fromJson(message['message']);
        if (message['message'].winner === undefined){
            message['message'].winner = {'firstName' : 'Nobody'};
        };
    };
    
    $scope.closeMessagesScreen = function () {
        $rootScope.showMessages = false;
    };
    
    $scope.closeMessage = function (message) {
        angular.element('#message-'+message['id']).remove();
    };
    
    $scope.readMessage = function (message) {
        data = {};
        message['status'] = 'Read';
        objects=[{'message':message}];
        data['objects'] = objects;
        $http.
            put(message['resource_uri'], data).success(function(data) {
                if (data) {
                    angular.element('#message-'+message['id']).remove();
                }
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


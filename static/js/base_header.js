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

function userDetailsCtrl($scope, $rootScope, $http) {

    //initialization
    $rootScope.user = {};
    $rootScope.user.displayName = '';
    $rootScope.user.profileFotoLink = '';
    $rootScope.user.profileLink = '';
    $rootScope.user.tokens = 0;
    $rootScope.user.credits = 0;

    //define channel
    $scope.realtimeStatus = "Connecting...";
    $scope.channel = "/topic/main/";
    $scope.limit = 20;
    
    //API request get user details
    $http
        .post('/api/getUserDetails/')
        .success(function (user) {
            $rootScope.user = user;
        });

    $rootScope.$on('reloadUserDataEvent', function () {
        $http
            .post('/api/getUserDetails/')
            .success(function (user) {
                $scope.user.tokens = user.tokens;
                $scope.user.credits = user.credits;
            });
    });

    $rootScope.$on('openGetCreditsPopover', function () {
        showOverlay();
        setTimeout(function () {
            jQuery('.buy-bids-popup').show();
            TweenLite.fromTo('.buy-bids-popup', 1, {left: '50px'},{left: '150x', ease: Back.easeOut});
        }, 300);
    });

    $rootScope.$on('closeGetCreditsPopover', function () {
        hideOverlay();
        TweenLite.to('.buy-bids-popup', 1, {left: '-800px', onComplete: function () {
            jQuery('.buy-bids-popup').hide();
        }})
    });

    $rootScope.$on('user:friendJoined', $scope.showJoinedFriendsDialog);

    $scope.showJoinedFriendsDialog = function (event, data) {
        $scope.joinedFriendsData = data;
    };

    $scope.hideJoinedFriendsDialog = function (showInviteMoreFriends) {
        $scope.joinedFriendsData = null;
        if (showInviteMoreFriends) {
            $scope.sendRequestViaMultiFriendSelector();
        }
    };

    $scope.convertChips = function() {
        $http.post('/api/convert_tokens/', {'amount': jQuery('#tokens_to_convert').val()}).success(
            function (data, status) {
                $rootScope.$emit('reloadUserDataEvent');

                jQuery('#user_bids').text(data.bids);
                jQuery('#user_tokens').text(data.tokens);
                jQuery('#convertible_tokens').text(data.tokens);
                jQuery('#maximun_bidsto').text(data.maximun_bidsto);
                var options = '';
                for (var i = 0; i < data.convert_combo.length; i++) {
                    options += '<option value="' + data.convert_combo[i] + '">' + data.convert_combo[i] + '</option>';
                }
                jQuery('select#tokens_to_convert').html(options);
            });
    };

    $scope.shareOnTimeline = function () {
        FB.ui({
            method: 'feed',
            link: 'https://apps.facebook.com/ibidgames/'
        });
    };

    $scope.sendRequestViaMultiFriendSelector = function() {
        FB.ui({method: 'apprequests',
            message: 'Come join me to play and win amazing deals at iBidGames!'
        }, $scope.sendRequestViaMultiFriendSelectorCallback);
    };

    $scope.sendRequestViaMultiFriendSelectorCallback = function(data) {
        console.log(data);
        if (data != null) {
            openPopupFrendsInvited();
            //store invitations
            $http.post('/api/inviteRequest/', {'invited': data.to})
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
                }else{
                    jQuery('.button.like').removeClass('disabled');
                }});
    };
    
    $scope.fb_like= function() {
        $http.post('/fb_like/').success(
         function(data){
             switch (data['info']) {
                case 'FIRST_LIKE':
                    /*
                     * In this case the user receives tokens because is the first like.
                     * data['gift'] says the amount of tokens gifted.
                     */
                    jQuery('.button.like').addClass('disabled');
                    jQuery('.tokens').text('TOKENS: ' + data['tokens']);
                    break;
                case 'NOT_FIRST_LIKE':
                    /*
                     * In this case the user is liking but not for the first time.
                     * For example when the user stops liking in facebook and likes again.
                     * The user is not getting the tokens.
                     */
                    jQuery('.button.like').addClass('disabled');
                    break;
                case 'ALREADY_LIKE':
                    /*
                     * This is a case that occurs when the user already likes and facebook returns
                     * a error code 3501
                     */
                    break;
             }
         });
    };
    
};


jQuery(function () {
    jQuery('.buy-bids-popup').hide();
    jQuery('.friends-invited-popup').hide();
    jQuery('.close', '.friends-invited-popup').click(closePopupFriendsInvited);
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


function openPopupFrendsInvited() {
    showOverlay();
    setTimeout(function () {
        jQuery('.friends-invited-popup').show();
        TweenLite.fromTo('.friends-invited-popup', 1, {left: '-800px'},{left: '200px', ease: Back.easeOut});
    }, 300);
}
function closePopupFriendsInvited() {
    hideOverlay();
    TweenLite.to('.friends-invited-popup', 1, {left: '-800px', onComplete: function () {
        jQuery('.friends-invited-popup').hide()
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


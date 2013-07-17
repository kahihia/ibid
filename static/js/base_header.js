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


var userDetailsData = {
    displayName: '',
    tokens: 0,
    profileFotoLink: '',
    credits: 0,
    profileLink: ''
};

function userDetailsCtrl($scope, $rootScope, $http) {

    //initialization
    $rootScope.user = {};
    $rootScope.user.displayName = '';
    $rootScope.user.profileFotoLink = '';
    $rootScope.user.profileLink = '';
    $rootScope.user.tokens = 0;
    $rootScope.user.credits = 0;

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

};


jQuery(function () {
    jQuery('.buy-bids-popup').hide();
    jQuery('.btn-credits').click(openPopupBuyBids);
    jQuery('.close', '.buy-bids-popup').click(closePopupBuyBids);
    jQuery('.like-popup').hide();
    jQuery('.like').click(openPopupLike);
    jQuery('.close', '.like-popup').click(closePopupLike);
    jQuery('.friends-invited-popup').hide();
    jQuery('.close', '.friends-invited-popup').click(closePopupFriendsInvited);
})

var underlay = '.underlay';
var popupClass = '.popup';
var popupOuter = '.popup-outer';


function openPopupBuyBids() {
    console.log('openPopupBuyBids');
    showOverlay();
    setTimeout(function () {
        jQuery('.buy-bids-popup').show();
        TweenLite.fromTo('.buy-bids-popup', 1, {left: '50px'},{left: '150x', ease: Back.easeOut});
    }, 300);
}

function closePopupBuyBids() {
    console.log('closePopupBuyBids');
    hideOverlay();
    TweenLite.to('.buy-bids-popup', 1, {left: '-800px', onComplete: function () {
        jQuery('.buy-bids-popup').hide()
    }})
}

function openPopupLike() {
    showOverlay();
    setTimeout(function () {
        jQuery('.like-popup').show();
        TweenLite.fromTo('.like-popup', 1, {left: '-800px'},{left: '200px', ease: Back.easeOut});
    }, 300);
}

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

                    FB.ui(obj, buyBids_callback);
                }
            }
        }, 'json');
}

var buyBids_callback = function (data) {
    if (data['order_id']) {
        refresh_user_bids();
        return true;
    } else {
        // handle errors here
        return false;
    }
};


function openPopupLike() {
    showOverlay();
    setTimeout(function () {
        jQuery('.like-popup').show();
        TweenLite.fromTo('.like-popup', 1, {left: '-800px'},{left: '200px', ease: Back.easeOut});
    }, 300);
}
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


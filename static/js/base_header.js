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
    $http.post('/api/getUserDetails/').
        success(function (rdata, status) {
            console.log('userDetailsCtrl')
            console.log(rdata)
            $rootScope.user = {};
            $rootScope.user.displayName = rdata.displayName;
            $rootScope.user.profileFotoLink = rdata.profileFotoLink;
            $rootScope.user.profileLink = rdata.profileLink;
            $rootScope.user.tokens = rdata.tokens;
            $rootScope.user.credits = rdata.credits;
        });

    $rootScope.$on('reloadUserDataEvent', function () {

        $http.post('/api/getUserDetails/').
            success(function (rdata, status) {
                $scope.user.tokens = rdata.tokens;
                $scope.user.credits = rdata.credits;
            });
    });
};


jQuery(function () {
    //jQuery('.buy-bids-popup').center();
    jQuery('.buy-bids-popup').hide();
    jQuery('.btn-credits').click(openPopupBuyBids);
    jQuery('.close', '.buy-bids-popup').click(closePopupBuyBids);
    jQuery('.invite').click(sendRequestViaMultiFriendSelector);
   // jQuery('.like-popup').center();
    jQuery('.like-popup').hide();
    jQuery('.like').click(openPopupLike);
    jQuery('.close', '.like-popup').click(closePopupLike);

    //jQuery('.friends-invited-popup').center();
    jQuery('.friends-invited-popup').hide();
    jQuery('.close', '.friends-invited-popup').click(closePopupFriendsInvited);

    //jQuery('').click()
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

    $.post(url, {'package_id': package_id},
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

function convertChips() {

    $.post('/api/convert_tokens/', {'amount': $('#tokens_to_convert').val()},
        function (data) {
            $('#user_bids').text(data.bids);
            $('#user_tokens').text(data.tokens);
            $('#convertible_tokens').text(data.tokens);
            $('#maximun_bidsto').text(data.maximun_bidsto);
            var options = '';
            for (var i = 0; i < data.convert_combo.length; i++) {
                options += '<option value="' + data.convert_combo[i] + '">' + data.convert_combo[i] + '</option>';
            }
            $('select#tokens_to_convert').html(options);
        }, 'json');
};


function sendRequestViaMultiFriendSelector() {
  FB.ui({method: 'apprequests',
    message: 'Come join me to play and win amazing deals at iBidGames!'
  }, sendRequestViaMultiFriendSelectorCallback);
}
function sendRequestViaMultiFriendSelectorCallback(data){
    console.log(data);
    if(data != null){
        openPopupFrendsInvited();
    }
}

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


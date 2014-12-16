function sendRequestViaMultiFriendSelector(auction_id, item_name, callback_url) {
	FB.ui({
		method : 'apprequests',
		message : 'Come join the auction for the ' + item_name + '!',
		title : 'Invite your friends to join the auction',
		filters : [ 'all' ],
	}, function(data) {
		store_invitation(callback_url, auction_id, data.request);
	});
}

function store_invitation(url, auction_id, request_id) {
	$.post(url, {
		'auction_id' : auction_id,
		'request_id' : request_id
	});
}

function buy_bids(url, package_id) {
    var order_info = -1;
	
    $.post(url, {'package_id': package_id},
        function (data) {
            if (data.order_info != undefined) {
                if (data.order_info >= 0) {

                    // calling the API ...
                    var obj = {
                        method : 'pay',
                        order_info : data.order_info,
                        purchase_type : 'item',
                        dev_purchase_params : {
                            'oscif' : true
                        }
                    };

                    FB.ui(obj, callback);
                }
            }
        }, 'json');
}

var callback = function(data) {
	if (data['order_id']) {
		refresh_user_bids();
		return true;
	} else {
		// handle errors here
		return false;
	}
};
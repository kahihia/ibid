angular
    .module('app', ['app.directives', 'app.services'])
    .run(function ($rootScope, $http) {
        // Declare basic variables.
        $rootScope.AUCTION_TYPE_CREDITS = 'credit';
        $rootScope.AUCTION_TYPE_TOKENS  = 'token';
        // dispatcher
        var eventMessage = new MessageEvent(MessageEvent.EVENT.BIDDING__INITIALIZE, {}, MessageEvent.SENDER.CLIENT_FB, MessageEvent.RECEIVER.SERVER, MessageEvent.TRANSPORT.REQUEST, getCurrentDateTime(), null);

        console.log({events: angular.toJson([eventMessage])});
        $http
            .get('/action/', {params: {events: angular.toJson([eventMessage])}})
            .then(function (response) {
                //listener - TRANSPORT request
                _.forEach(response.data, function (message) {
                    $rootScope.$broadcast(message.event, message.data);
                });
            });
    });

//listener - PUBNUB request


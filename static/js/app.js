angular
    .module('app', ['app.config', 'app.directives', 'app.services'])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    })
    .run(function ($rootScope, $http) {
        // Declare basic variables.
        $rootScope.AUCTION_TYPE_CREDITS = 'credit';
        $rootScope.AUCTION_TYPE_TOKENS  = 'token';
        // dispatcher
        var eventMessage = new EventMessage(EventMessage.EVENT.BIDDING__INITIALIZE, {}, EventMessage.SENDER.CLIENT_FB, EventMessage.RECEIVER.SERVER, EventMessage.TRANSPORT.REQUEST, getCurrentDateTime(), null);

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


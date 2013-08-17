angular
    .module('app', ['app.directives', 'app.services'])
    .run(function ($rootScope, $http) {
        // dispatcher
        var eventMessage = new Event(Event.prototype.EVENT.BIDDING__INITIALIZE, {}, Event.prototype.SENDER.CLIENT_FB, Event.prototype.RECEIVER.SERVER, Event.prototype.TRANSPORT.REQUEST, getCurrentDateTime(), null);

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


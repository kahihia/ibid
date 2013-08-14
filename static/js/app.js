angular
    .module('app', ['app.directives', 'app.services'])
    .run(function ($rootScope, $http) {
        // Declare basic variables.
        $rootScope.AUCTION_TYPE_CREDITS = 'credit';
        $rootScope.AUCTION_TYPE_TOKENS  = 'token';
        // Request initial data.
        $http
            .get('/action/initialize')
            .then(function (response) {
                _.forEach(response.data, function (message) {
                    $rootScope.$broadcast(message.event, message.data);
                });
            });
    });

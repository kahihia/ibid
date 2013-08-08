angular
    .module('app', ['app.services'])
    .run(function ($rootScope, $http) {
        $http
            .get('/action/initialize')
            .then(function (response) {
                _.forEach(response.data, function (message) {
                    $rootScope.$broadcast(message.event, message.data);
                });
            });
    });

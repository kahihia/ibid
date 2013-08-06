angular
    .module('app', [])
    .factory('api', function ($http) {
        var API_URL = '/';

        return {
            getInitializationData: function () {
                //since $http.get returns a promise,
                //and promise.then() also returns a promise
                //that resolves to whatever value is returned in it's
                //callback argument, we can return that.
                return $http
                            .get(API_URL + 'action/initialize')
                            .then(function (result) {
                                _.forEach(result, function (message) {
                                    switch (message.event) {
                                    case 'main:friendInvitationAccepted':
                                        console.log('!!!!!!');
                                        $rootScope.$broadcast('user:friendAcceptedInvitation', message.data);
                                        break;
                                    }
                                });
                            });
            }
        };
    });

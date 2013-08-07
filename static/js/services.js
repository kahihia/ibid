angular
    .module('app', [])
    .run(function ($rootScope, $http) {
        $http
            .get('/action/initialize')
            .then(function (response) {
                _.forEach(response.data, function (message) {
                    switch (message.event) {
                    case 'main:friendInvitationAccepted':
                        console.log('---emitted event');
                        $rootScope.$broadcast('user:friendAcceptedInvitation', message.data);
                        break;
                    }
                });
            });
    });

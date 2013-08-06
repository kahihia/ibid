angular
    .module('app', [])
    .run(function ($rootScope, $http) {
        $http
            .get('/action/initialize')
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
    });

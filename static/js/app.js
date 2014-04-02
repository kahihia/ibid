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
        
        $http.post('/api/getTemplateContext/').success(function (data) {
            //$rootScope.PUBNUB_PUB = data.PUBNUB_PUB;
            //$rootScope.PUBNUB_SUB = data.PUBNUB_SUB;
            $rootScope.MIXPANEL_TOKEN = data.MIXPANEL_TOKEN;
            $rootScope.SITE_NAME = data.SITE_NAME;
            $rootScope.FB_APP_ID = data.FB_APP_ID;
            $rootScope.SITE_NAME_WOUT_BACKSLASH = data.SITE_NAME_WOUT_BACKSLASH;

            window.fbAsyncInit = function() {
                FB.init({
                    appId : $rootScope.FB_APP_ID,
                    channelUrl : $rootScope.SITE_NAME_WOUT_BACKSLASH + '//connect.facebook.net/en_US/all.js', // Channel File
                    status     : true, // check login status
                    cookie     : true, // enable cookies to allow the server to access the session
                    xfbml      : true  // parse XFBML
                });
                $rootScope.$emit('InitializeGlobalChat');
                $rootScope.$emit('InitializeUvTabPosition');
                FB.Canvas.setAutoGrow();
            }; ( function(d, s, id) {
                    var js, fjs = d.getElementsByTagName(s)[0];
                    if (d.getElementById(id)) {
                         return;
                    }
                    js = d.createElement(s);
                    js.id = id;
                    js.src = "//connect.facebook.net/en_US/all.js";
                    fjs.parentNode.insertBefore(js, fjs);
                }(document, 'script', 'facebook-jssdk'));
        });
            
        //initialize analythics.js with mixpanel
        analytics.initialize({
            'Mixpanel' : {
                token  : $rootScope.MIXPANEL_TOKEN,
                people : true
            },
        });
        
        // API request get user details
        $http.post('/api/getUserDetails/').success(function (data) {
            // identify users
            analytics.identify(data.user.username, {
                email: data.user.email,
                name : data.user.first_name,
                last_name : data.user.last_name,
                fb_id : data.user.facebookId
            });
            $rootScope.user = data.user;
            $rootScope.convertTokens.tokenValueInCredits = data.app.tokenValueInCredits;
<<<<<<< HEAD
            $rootScope.subscribeToPaymentChannel($rootScope.user);
=======
>>>>>>> 364b3d97b064c987f726638e449ae26453b85fd6
        });
        
        // API request get user notifications
        $http
            .get('/api/v1/notification/')
            .success(function (notifications) {
                $rootScope.messageList = notifications.objects;
                if ($rootScope.messageList.length > 0) {
                    $rootScope.showMessages = true;
                } else {
                    $rootScope.showMessages = false;
                }
        });
        
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


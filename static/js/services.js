(function () {
    'use strict';

    angular
        .module('app.services', [])
        .factory('pubSub', function () {
            return {
                subscribe: function (options) {
                    _.defaults(options, {
                        connect: function () {
                            console.log('pubSub service: channel %s connected', options.channel);
                        },
                        message: function (messages) {
                            _.forEach(messages, function (message) {
                                console.log('pubSub service: channel %s message (%s)', options.channel, getCurrentDateTime(), message);
                            });
                        },
                        reconnect: function () {
                            console.log('pubSub service: channel %s reconnected', options.channel);
                        },
                        disconnect: function () {
                            console.log('pubSub service: channel %s disconnected', options.channel);
                        },
                        error: function (data) {
                            console.log('pubSub service: channel %s network error', options.channel, data);
                        }
                    });
                    return PUBNUB.subscribe(options);
                },
                unsubscribe: function (channel) {
                    return PUBNUB.unsubscribe({channel: channel});
                }
            };
        })
        .factory('notification', function ($rootScope, $document, $templateCache, $compile, $timeout) {
            return {
                show: function (message) {
                    // Get the template from $templateCache.
                    var template = $templateCache.get('template/notification.html');
                    // Create new scope for $compile.
                    var scope = $rootScope.$new();
                    scope.message = message;
                    // Compile template and append to DOM.
                    var el = $compile(template)(scope);
                    $document.find('#notifications').append(el);
                    $timeout(function () {
                        el.remove();
                    }, 10000);
                }
            };
        });
}());

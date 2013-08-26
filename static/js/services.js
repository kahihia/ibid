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
        });
}());

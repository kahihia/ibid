'use strict';

angular
    .module('app.config', [])
    .provider('config', function (configValues) {
        this.$get = function () {
            return {
                get: function (key) {
                    return configValues[key];
                }
            };
        };
    });

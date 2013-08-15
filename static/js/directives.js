(function () {
    'use strict';

    angular
        .module('app.directives', [])
        .directive('ibAutoscroll', function () {
            return {
                require: 'ngModel',
                link: function postLink (scope, element, attributes, ngModel) {
                    scope.$watch(
                        angular.identity(ngModel.$modelValue),
                        function () {
                            element.scrollTop(element.get(0).scrollHeight);
                        },
                        true
                    );
                }
            };
        })
        .directive('dialog', function () {
            return {
                replace: true,
                restrict: 'E',
                scope: {
                    title: '@dialogTitle'
                },
                templateUrl: '/static/templates/dialog.html',
                transclude: true//,
                // link: function postLink (scope, element, attributes) {}
            };
        });
}());

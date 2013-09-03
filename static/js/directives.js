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
        .directive('ibTransitionClass', function ($timeout) {
            return {
                link: function postLink (scope, element, attributes) {
                    var oldVals;
                    scope.$watch(angular.identity(attributes.ibTransitionClass), function () {
                        angular.forEach(scope.$eval(attributes.ibTransitionClass), function (value, key) {
                            if (!oldVals || !oldVals.hasOwnProperty(key) || !angular.equals(value, oldVals[key])) {
                                element.removeClass(key);
                                $timeout(function () {
                                    element.addClass(key);
                                });
                            }
                        });
                        oldVals = angular.copy(attributes.ibTransitionClass);
                    },
                    true);
                }
            };
        });
        // .directive('modal', function () {
        //     return {
        //         replace: true,
        //         restrict: 'E',
        //         scope: {
        //             title: '@dialogTitle'//,
        //             // closeButton: '@dialogClose',
        //             // closeClass: '@dialogCloseClass'
        //         },
        //         templateUrl: '/static/template/dialog.html',
        //         transclude: true//,
        //         // link: function postLink (scope, element, attributes) {
        //                // Alternative
        //         //     scope.title = attributes.dialogTitle;
        //         //     scope.close = attributes.dialogClose;
        //         //     scope.closeClass = attributes.dialogCloseClass;
        //         // }
        //     };
        // });
}());

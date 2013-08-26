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

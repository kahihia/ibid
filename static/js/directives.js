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
        })
        .directive('ibTour', ['$rootScope', '$window', function ($rootScope, $window) {
            console.log($window);

            var defaults = {
                autoStart: true,
                cookieMonster: true,
                scroll: false,
                template: {
                    link: '<a href="#close" class="joyride-close-tip">×</a>',
                    button: '<a href="#" class="joyride-next-tip btn"></a>',
                    wrapper: '<div class="joyride-content-wrapper" role="dialog"><img class="joyride-kenny" src="/static/images/tooltip-action-kenny.png" alt=""></div>'
                }
            };

            return {
                restrict: 'A',
                link: function postLink (scope, element, attrs) {
                    var opts = _.extend({}, defaults, {
                        postRideCallback: function () {
                            element.joyride('destroy');
                        }
                    });
                    if (attrs.ibTourCookie && attrs.ibTourCookie === false) {
                        console.log('no cookie!!');
                        _.extend(opts, {cookieMonster: false});
                    }
                    else if ($.cookie(attrs.id) === 'ridden') {
                        console.log('ridden!!!');
                        return;
                    }
                    else {
                        _.extend(opts, {cookieName: attrs.id});
                    }
                    if (attrs.ibTourButtonTriggers) {
                        _.extend(opts, {
                            postStepCallback: function () {
                                scope.$apply(function (scope) {
                                    scope.$emit(attrs.ibTourButtonTriggers);
                                });
                            }
                        });
                    }
                    if (attrs.ibTourTriggerEvent) {
                        $rootScope.$on(attrs.ibTourTriggerEvent, function () {
                            element.joyride(opts);
                        });
                    }
                    else {
                        element.joyride(opts);
                    }
                }
            };
        }]);
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

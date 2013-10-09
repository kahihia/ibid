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
            // WARNING:
            // This is awkward but this directive needs the currently
            // commited version of jquery.joyride-2.1.js because it
            // has been edited to have one or two features needed for
            // this implementation. So don't replace/update it.

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
                            // Destroy tour after ending it to avoid
                            // some problems.
                            element.joyride('destroy');
                        }
                    });

                    // If has attribute ib-tour-cookie="false",
                    // doesn't writes cookie so that tip can be
                    // displayed everytime.
                    if (attrs.ibTourCookie && attrs.ibTourCookie === 'false') {
                        _.extend(opts, {cookieMonster: false});
                    }
                    // Else, check if cookie is already there, if it
                    // is, do nothing.
                    else if ($.cookie(attrs.id) === 'ridden') {
                        return;
                    }
                    // Else, set cookie name to the id of the tour.
                    else {
                        _.extend(opts, {cookieName: attrs.id});
                    }

                    // If has a ib-tour-button-fires-event attribute,
                    // bind postStepCallback event handler to fire an
                    // event when clicking the tip button.
                    if (attrs.ibTourButtonFiresEvent) {
                        _.extend(opts, {
                            postStepCallback: function (i, tipEl, isAborted) {
                                if (!isAborted) {
                                    // Only if tour is not aborted.
                                    scope.$emit(attrs.ibTourButtonFiresEvent);
                                    // Trigger digest cycle if not
                                    // in one currently.
                                    if (!scope.$$phase) {
                                        scope.$apply();
                                    }
                                }
                            }
                        });
                    }

                    // If has a ib-tour-trigger-on-event attribute,
                    // activates when that event is fired.
                    if (attrs.ibTourTriggerOnEvent) {
                        var unBindEvent = $rootScope.$on(attrs.ibTourTriggerOnEvent, function () {
                            // Check cookies to see if tip was already
                            // displayed. If it was, unbind this event
                            // handler and return.
                            if ($.cookie(attrs.id) === 'ridden') {
                                unBindEvent();
                                return;
                            }
                            element.joyride(opts);
                        });
                    }
                    else {
                        // Normal plugin activation.
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

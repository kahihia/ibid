angular
  .module('app.directives', [])
  .directive('ibAutoscroll', function () {
    return {
      require: 'ngModel',
      link: function (scope, element, attributes, ngModel) {
        scope.$watch(function () {
          return ngModel.$modelValue;
        }, function () {
          element.scrollTop(element.get(0).scrollHeight);
        },
        true);
      }
    };
  });

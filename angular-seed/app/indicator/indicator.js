'use strict';

var app = angular.module('myApp.indicator', ['ngRoute']);

app.controller(
  'IndicatorDialogCtrl',
  ['indicator', '$mdDialog', '$resources', '$scope',
    function (indicator, $mdDialog, $resources, $scope) {

      this.cancel = $mdDialog.cancel;

      $scope.indicator = JSON.parse(JSON.stringify(indicator));

      this.saveIndicator = function () {
        var data = {
          'value': $scope.indicator.value,
        };
        $scope.promise = $resources.indicators.update(
          { 'indicator_id': $scope.indicator.id },
          data,
          function (indicator) {
            $mdDialog.hide(indicator);
          }).$promise;
      }

    }]);

app.directive('indicators', function () {
  return {
    scope: {
      resource: '=',
      queryParams: '=',
      showApartmentNumber: '@showApartmentNumber',
      refresh: '='
    },
    templateUrl: 'indicator/indicators-directive.html',
    controller: ['$scope', '$resources', '$mdDialog', '$mdEditDialog', 'moment', '$location',
      function ($scope, $resources, $mdDialog, $mdEditDialog, moment, $location) {

        $scope.selected = [];

        $scope.filter = {
          options: {
            debounce: 500
          }
        };

        $scope.query = {
          filter: '',
          limit: '5',
          order: 'meter__apartment__address__apartment__number',
          page: 1,
          period: new Date(moment({ day: 1 }).format("YYYY-MM-DD")),
        };

        angular.extend($scope.query, $scope.queryParams);

        $scope.refresh = function () {
          $scope.getIndicators();
        }

        $scope.getIndicators = function () {
          $scope.promise = $scope.resource.get(
            $scope.query,
            function (indicators) {
              $scope.indicators = indicators;
            }
          ).$promise;
        };

        $scope.$watch(
          'query.period',
          function (newValue, oldValue) {
            $scope.refresh();
          }
        );

        $scope.viewApartmentDetails = function (event, apartment) {
          event.stopPropagation();
          $location.path('/apartments/' + apartment.id + '/');
        }

        $scope.editIndicator = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'IndicatorDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { indicator: $scope.selected[0] },
            templateUrl: 'indicator/indicator-dialog.html',
          }).then($scope.refresh);
        };

        $scope.editIndicatorInline = function (event, indicator) {

          self = this;

          event.stopPropagation();

          this.saveIndicator = function (indicator) {
            var data = {
              'value': indicator.value,
            };
            $scope.promise = $resources.indicators.update(
              { 'indicator_id': indicator.id },
              data,
              function (indicator) {
                $mdDialog.hide(indicator);
              }).$promise;
          }

          var promise = $mdEditDialog.large({
            'title': 'Показник',
            'cancel': 'Відмінити',
            'ok': 'Зберегти',
            messages: {
              test: ' '
            },
            'type': 'number',
            modelValue: indicator.value,
            placeholder: 'Введіть показник',
            save: function (input) {
              indicator.value = input.$modelValue;
              self.saveIndicator(indicator);
            },
            targetEvent: event
          });

          promise.then(function (ctrl) {
            var input = ctrl.getInput();

            input.$viewChangeListeners.push(function () {
              input.$setValidity('test', input.$modelValue !== 'test');
            });
          });
        }
      }]
  };
});

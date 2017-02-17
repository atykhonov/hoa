'use strict';

var app = angular.module('myApp.indicator', ['ngRoute']);

app.config([
  '$routeProvider',
  function ($routeProvider) {
    $routeProvider.when('/indicators', {
      templateUrl: 'indicator/indicator.html',
      controller: 'IndicatorCtrl'
    });
  }]);

app.controller(
  'IndicatorCtrl', [
    '$mdDialog', '$resources', '$scope', '$location', 'auth', '$mdEditDialog', 'moment',
    function ($mdDialog, $resources, $scope, $location, auth, $mdEditDialog, moment) {

      var bookmark;

      var userInfo = auth.getUserInfo();
      var associationId = userInfo['cooperative_id'];

      $scope.selected = [];

      $scope.filter = {
        options: {
          debounce: 500,
        }
      };

      $scope.query = {
        filter: '',
        limit: '6',
        order: 'id',
        page: 1,
        period: new Date(moment({ day: 1 }).format("YYYY-MM-DD")),
      };

      $scope.viewApartments = function (event, house_id) {
        $location.url('/houses/' + house_id + '/apartments/');
      }

      $scope.addIndicator = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddHouseController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'house/add-house-dialog.html',
        }).then($scope.getHouses);
      };

      $scope.deleteIndicator = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteHouseController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { houses: $scope.selected },
          templateUrl: 'house/delete-dialog.html',
        }).then($scope.getHouses);
      };

      $scope.editIndicator = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditHouseController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { house: $scope.selected[0] },
            templateUrl: 'house/add-house-dialog.html',
          }).then($scope.getHouses);
        }
      };

      $scope.viewMeter = function (meter, event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'MeterController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: { meter: meter },
          templateUrl: 'indicator/view-meter-dialog.html',
        });
      }

      $scope.editComment = function (event, indicator) {

        var self = this;

        event.stopPropagation();

        function success(indicator) {
          var indicators = $scope.indicators.data;
          for (var i = 0; i < indicators.length; i++) {
            if (indicators[i].id == indicator.id) {
              indicators[i].date = moment(indicator.date);
              break;
            }
          }
        }

        this.saveIndicator = function (indicator) {
          var data = {
            'value': indicator.value,
          };
          $scope.promise = $resources.indicators.update(
            { 'indicator_id': indicator.id }, data, success).$promise;
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
      };

      function success(indicators) {
        $scope.indicators = indicators;
      }

      $scope.getIndicators = function () {
        var query = $scope.query;
        query['cooperative_id'] = associationId;
        $scope.promise = $resources.cooperative_indicators.get(
          $scope.query, success).$promise;
      };

      $scope.removeFilter = function () {
        $scope.filter.show = false;
        $scope.query.filter = '';

        if ($scope.filter.form.$dirty) {
          $scope.filter.form.$setPristine();
        }
      };

      $scope.$watch('query.period', function (newValue, oldValue) {
        $scope.getIndicators();
      });

    }]);

app.controller(
  'AddIndicatorController', [
    '$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(house) {
        $mdDialog.hide(house);
      }

      this.addHouse = function () {
        $scope.house['cooperative_id'] = associationId;
        $scope.promise = $resources.assoc_houses.create($scope.house, success).$promise;
      }
    }])

app.controller(
  'DeleteIndicatorController', [
    'houses', '$mdDialog', '$resources', '$scope', '$q',
    function (houses, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(houses.forEach(deleteHouse)).then(onComplete);
      }

      function deleteHouse(house, index) {
        var deferred = $resources.houses.delete({ id: house.id });

        deferred.$promise.then(function () {
          houses.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }]);

app.controller(
  'EditIndicatorController', [
    'house', '$mdDialog', '$resources', '$scope', '$q',
    function (house, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.house = JSON.parse(JSON.stringify(house));

      this.updateHouse = function () {
        var deferred = $resources.houses.update({ id: house.id }, $scope.house);
        deferred.$promise.then(function () {
          $mdDialog.hide(house);
        });
        return deferred.$promise;
      }

    }]);

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

app.controller(
  'MeterController',
  ['meter', '$mdDialog', '$resources', '$scope',
    function (meter, $mdDialog, $resources, $scope) {

      $scope.myDate = new Date(2017, 1, 1);
    }]);

app.directive('indicators', function () {
  return {
    scope: {
      resource: '=',
      queryParams: '=',
      showApartmentNumber: '@showApartmentNumber'
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
          order: 'id',
          page: 1,
          period: new Date(moment({ day: 1 }).format("YYYY-MM-DD")),
        };

        angular.extend($scope.query, $scope.queryParams);

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
            $scope.getIndicators();
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
          }).then($scope.getIndicators);
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

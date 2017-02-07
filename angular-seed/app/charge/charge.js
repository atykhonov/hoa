'use strict';

var app = angular.module('myApp.charge', ['ngRoute'])

app.config([
  '$routeProvider',
  function ($routeProvider) {
    $routeProvider.when('/charges', {
      templateUrl: 'charge/charge.html',
      controller: 'ChargeCtrl'
    });
  }]);

app.controller(
  'ChargeCtrl', [
    '$mdDialog', '$resources', '$scope', '$routeParams', 'auth', 'moment',
    function ($mdDialog, $resources, $scope, $routeParams, auth, moment) {

      var bookmark;

      var userInfo = auth.getUserInfo();
      var associationId = userInfo['cooperative_id'];

      $scope.months = {
        1: 'січень',
        2: 'лютий',
        3: 'березень',
        4: 'квітень',
        5: 'травень',
        6: 'червень',
        7: 'липень',
        8: 'серпень',
        9: 'вересень',
        10: 'жовтень',
        11: 'листопад',
        12: 'грудень',
      };

      $scope.now = moment.now();

      $scope.years = [
        2016, 2017, 2018
      ];

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
        page: 1
      };

      function success(response) {
        var charges = [];
        angular.forEach(response.data, function (charge, id) {
          var item = {
            'id': charge.id,
            'pid': charge.pid,
            'address': charge.address,
            'service_charges': [],
            'total': charge.total
          };
          angular.forEach($scope.services, function (service) {
            var service_charge_value = 0;
            angular.forEach(charge.services, function (service_charge, id) {
              if (service_charge.service.id == service.id) {
                service_charge_value = service_charge.value;
              }
            });
            item['service_charges'].push({
              'value': service_charge_value
            });
          });
          charges.push(item);
        });
        charges.count = response.count;
        $scope.charges = charges;
      }

      function success_services(response) {
        var services = [];
        angular.forEach(response.data, function (assoc_service, id) {
          services.push({
            'id': assoc_service.service.id,
            'name': assoc_service.service.name
          });
        });
        $scope.services = services;
        $scope.getCharges();
      }

      $scope.getCharges = function () {
        var query = $scope.query;
        $scope.promise = $resources.charges.get($scope.query, success).$promise;
      };

      $scope.getServices = function () {
        $scope.services_promise = $resources.cooperative_services.get(
          { cooperative_id: associationId }, success_services).$promise;
      }

      $scope.removeFilter = function () {
        $scope.filter.show = false;
        $scope.query.filter = '';

        if ($scope.filter.form.$dirty) {
          $scope.filter.form.$setPristine();
        }
      };

      $scope.calcCharges = function (event) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
          .title('Перерахувати нарахування?')
          .textContent('Усі нарахування за поточний місяць будуть перераховані.')
          // .ariaLabel('Lucky day')
          .targetEvent(event)
          .ok('Перерахувати')
          .cancel('Скасувати');

        $mdDialog.show(confirm).then(function () {
          $resources.cooperative_recalccharges.create({ cooperative_id: associationId });
        }, function () {
        });
      };

      $scope.$watch('query.filter', function (newValue, oldValue) {
        if (!oldValue) {
          bookmark = $scope.query.page;
        }

        if (newValue !== oldValue) {
          $scope.query.page = 1;
        }

        if (!newValue) {
          $scope.query.page = bookmark;
        }

        $scope.getServices();
      });

    }]);

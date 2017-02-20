'use strict';

var app = angular.module('myApp.charge', ['ngRoute'])

app.directive('charges', function () {
  return {
    scope: {
      resource: '=',
      servicesResource: '=',
      recalcChargesResource: '=',
      recalcChargesCallback: '=',
      queryParams: '=',
      showPersonalAccount: '@showPersonalAccount'
    },
    templateUrl: 'charge/charges-directive.html',
    controller: ['$scope', '$resources', '$mdDialog', '$mdEditDialog', '$location', 'auth',
      function ($scope, $resources, $mdDialog, $mdEditDialog, $location, auth) {

        $scope.filter = {
          options: {
            debounce: 500
          }
        };

        $scope.query = {
          filter: '',
          limit: '5',
          order: 'account__id',
          page: 1
        };

        var userInfo = auth.getUserInfo();
        $scope.recalculatable = false;
        if (userInfo['superuser'] || userInfo['manager']) {
          $scope.recalculatable = true;
        }

        $scope.servicesQuery = {
        };

        angular.extend($scope.query, $scope.queryParams);
        angular.extend($scope.servicesQuery, $scope.queryParams);

        function success(response) {
          var charges = [];
          angular.forEach(response.data, function (charge, id) {
            var item = {
              'id': charge.id,
              'pid': charge.pid,
              'address': charge.address,
              'service_charges': [],
              'total': charge.total,
              'apartment_id': charge.account.apartment.id
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
          $scope.promise = $scope.resource.get($scope.query, success).$promise;
        };

        $scope.getServices = function () {
          $scope.promise = $scope.servicesResource.get(
            $scope.servicesQuery, success_services).$promise;
        }

        $scope.calcCharges = function (event) {
          var confirm = $mdDialog.confirm()
            .title('Перерахувати нарахування?')
            .textContent('Усі нарахування за поточний місяць будуть перераховані!')
            .targetEvent(event)
            .ok('Перерахувати')
            .cancel('Скасувати');

          $mdDialog.show(confirm).then(function () {
            $scope.promise = $scope.recalcChargesResource.recalc($scope.query, function () {
              $scope.getServices();
              if ($scope.recalcChargesCallback) {
                $scope.recalcChargesCallback();
              }
            });
          }, function () {
          });
        };

        $scope.viewAccountDetails = function (event, apartmentId) {
          event.stopPropagation();
          $location.path('/apartments/' + apartmentId + '/account/');
        }

        $scope.getServices();
      }]
  }
});

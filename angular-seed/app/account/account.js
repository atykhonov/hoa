'use strict';

var mod = angular.module('myApp.account', ['ngRoute']);

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/apartments/:apartmentId/account/', {
    templateUrl: 'account/account-details.html',
    controller: 'AccountDetailsCtrl'
  });
}]);

mod.controller(
  'AccountDialogCtrl',
  ['account', '$mdDialog', '$resources', '$scope',
    function (account, $mdDialog, $resources, $scope) {

      this.cancel = $mdDialog.cancel;

      $scope.account = JSON.parse(JSON.stringify(account));

      this.saveAccount = function () {
        var deferred = $resources.accounts.update({ id: account.id }, $scope.account);
        deferred.$promise.then(function (response) {
          $mdDialog.hide(response);
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'AccountDetailsCtrl',
  ['$scope', '$resources', '$routeParams', '$mdDialog', 'moment', '$mdEditDialog', 'breadcrumb',
    function ($scope, $resources, $routeParams, $mdDialog, moment, $mdEditDialog, breadcrumb) {

      breadcrumb.init($routeParams);

      var apartmentId = $routeParams.apartmentId;

      $scope.indicatorsResource = $resources.apartment_indicators;
      $scope.indicatorsQueryParams = {
        apartment_id: apartmentId
      };

      $scope.chargesResource = $resources.apartment_charges;
      $scope.servicesResource = $resources.apartment_services;
      $scope.chargesQueryParams = {
        apartment_id: apartmentId
      };

      $scope.promise = $resources.apartments.get(
        { id: apartmentId },
        function (apartment) {
          $scope.apartment = apartment;
        }
      ).$promise;
    }]);

mod.directive('account', function () {
  return {
    scope: {
      model: '='
    },
    templateUrl: 'account/account-directive.html',
    controller: ['$scope', '$resources', '$mdDialog',
      function ($scope, $resources, $mdDialog) {

        $scope.$watch(
          'model',
          function (newValue, oldValue) {
            if (newValue) {
              $scope.account = newValue;
            }
          }
        );

        $scope.editAccount = function (event, account) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'AccountDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { account: account },
            templateUrl: 'account/account-dialog.html',
          }).then(function (account) {
            $scope.account = account;
          });
        };
      }]
  }
});

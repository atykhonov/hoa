'use strict';

var mod = angular.module('myApp.apartment', ['ngRoute'])

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/apartments/:apartmentId/', {
    templateUrl: 'apartment/apartment-details.html',
    controller: 'ApartmentDetailsCtrl'
  });
}]);

mod.controller(
  'ApartmentDetailsCtrl',
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
      $scope.recalcChargesResource = $resources.apartment_recalccharges;
      $scope.recalcChargesCallback = function () {
        $scope.getApartment();
      }

      $scope.chargesQueryParams = {
        apartment_id: apartmentId
      };

      $scope.getApartment = function () {
        $scope.promise = $resources.apartments.get(
          { id: apartmentId },
          function (apartment) {
            $scope.apartment = apartment;
          }
        ).$promise;
      }
      $scope.getApartment();
    }]);

mod.controller(
  'ApartmentDialogCtrl', [
    'apartment', '$mdDialog', '$resources', '$scope', 'auth',
    function (apartment, $mdDialog, $resources, $scope, auth) {

      this.cancel = $mdDialog.cancel;

      if ('id' in apartment) {
        $scope.apartment = JSON.parse(JSON.stringify(apartment));
      } else {
        $scope.apartment = {};
      }

      this.addApartment = function () {
        $scope.apartment['house_id'] = apartment['houseId'];
        $scope.promise = $resources.assoc_houses.create(
          $scope.apartment,
          function (apartment) {
            $mdDialog.hide(apartment);
          }
        ).$promise;
      }

      this.saveApartment = function () {
        var deferred = $resources.apartments.update({ id: apartment.id }, $scope.apartment);
        deferred.$promise.then(function (apartment) {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }
    }]);

mod.directive('apartment', function () {
  return {
    scope: {
      model: '='
    },
    templateUrl: 'apartment/apartment-directive.html',
    controller: ['$scope', '$resources', '$mdDialog',
      function ($scope, $resources, $mdDialog) {

        $scope.$watch(
          'model',
          function (newValue, oldValue) {
            if (newValue) {
              $scope.apartment = newValue;
            }
          }
        );

        $scope.editApartment = function (event, apartment) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ApartmentDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { apartment: apartment },
            templateUrl: 'apartment/apartment-dialog.html',
          }).then(function (apartment) {
            $scope.apartment = apartment;
          });
        };
      }]
  }
});

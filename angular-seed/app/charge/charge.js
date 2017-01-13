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
    '$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

      var bookmark;

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
        order: 'number',
        page: 1
      };

      $scope.addApartment = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddApartmentController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'apartment/add-apartment-dialog.html',
        }).then($scope.getApartments);
      };

      $scope.deleteApartment = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteApartmentController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { apartments: $scope.selected },
          templateUrl: 'apartment/delete-dialog.html',
        }).then($scope.getApartments);
      };

      $scope.editApartment = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditApartmentController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { apartment: $scope.selected[0] },
            templateUrl: 'apartment/add-apartment-dialog.html',
          }).then($scope.getApartments);
        }
      };

      $scope.editAccount = function (event, apartment_id) {

        event.stopPropagation();

        var apartment = undefined;
        var apartments = $scope.apartments.data;
        for (var i = 0; i < apartments.length; i++) {
          if (apartments[i].id == apartment_id) {
            apartment = apartments[i];
            break;
          }
        }
        console.log(apartment_id);
        console.log('Found apartment: ');
        console.log(apartment);
        console.log('All apartments: ');
        console.log(apartments);
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'EditApartmentAccountController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: { apartment: apartment },
          templateUrl: 'apartment/edit-account-dialog.html',
        }).then($scope.getApartments);
      }

      function success(charges) {
        $scope.charges = charges;
      }

      $scope.getCharges = function () {
        var query = $scope.query;
        if ($routeParams.id !== undefined) {
          query['house_id'] = $routeParams.id;
          $scope.promise = $resources.house_apartments.get(
            $scope.query, success).$promise;
        } else {
          $scope.promise = $resources.apartments.get(
            $scope.query, success).$promise;
        }
      };

      $scope.removeFilter = function () {
        $scope.filter.show = false;
        $scope.query.filter = '';

        if ($scope.filter.form.$dirty) {
          $scope.filter.form.$setPristine();
        }
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

        $scope.getCharges();
      });

    }]);

app.controller(
  'AddApartmentController', [
    '$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(apartment) {
        $mdDialog.hide(apartment);
      }

      this.addApartment = function () {
        $scope.apartment['house_id'] = $routeParams.id;
        $scope.promise = $resources.house_apartments.create($scope.apartment, success).$promise;
      }
    }]);

app.controller(
  'DeleteApartmentController', [
    'apartments', '$mdDialog', '$resources', '$scope', '$q',
    function (apartments, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(apartments.forEach(deleteApartment)).then(onComplete);
      }

      function deleteApartment(apartment, index) {
        var deferred = $resources.apartments.delete({ id: apartment.id });

        deferred.$promise.then(function () {
          apartments.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }]);

app.controller(
  'EditApartmentController', [
    'apartment', '$mdDialog', '$resources', '$scope', '$q',
    function (apartment, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.apartment = JSON.parse(JSON.stringify(apartment));

      this.updateApartment = function () {
        var deferred = $resources.apartments.update({ id: apartment.id }, $scope.apartment);
        deferred.$promise.then(function () {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }

    }]);

app.controller(
  'EditApartmentAccountController', [
    'apartment', '$mdDialog', '$resources', '$scope', '$q',
    function (apartment, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.updateAccount = function () {
        var deferred = $resources.apartment_account.update({ id: apartment.id }, $scope.account);
        deferred.$promise.then(function () {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }

    }]);

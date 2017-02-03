'use strict';

angular.module('myApp.apartment', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/houses/:id/apartments', {
      templateUrl: 'apartment/apartment.html',
      controller: 'ApartmentCtrl'
    });
    $routeProvider.when('/apartments', {
      templateUrl: 'apartment/apartment.html',
      controller: 'ApartmentCtrl'
    });
  }])

  .controller(
  'ApartmentCtrl',
  ['$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

      var bookmark;

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

      function success(apartments) {
        $scope.apartments = apartments;
      }

      $scope.getApartments = function () {
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

        $scope.getApartments();
      });

    }])

  .controller('AddApartmentController',
  ['$mdDialog', '$resources', '$scope', '$routeParams',
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
    }])

  .controller('DeleteApartmentController',
  ['apartments', '$mdDialog', '$resources', '$scope', '$q',
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

    }])

  .controller('EditApartmentController',
  ['apartment', '$mdDialog', '$resources', '$scope', '$q',
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

    }])

  .controller(
  'EditApartmentAccountController',
  ['apartment', '$mdDialog', '$resources', '$scope', '$q',
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

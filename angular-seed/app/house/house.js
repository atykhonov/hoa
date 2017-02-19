'use strict';

var mod = angular.module('myApp.house', ['ngRoute'])

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/houses/:houseId', {
    templateUrl: 'house/house-details.html',
    controller: 'HouseDetailsCtrl'
  });
}]);

mod.controller(
  'HouseModalCtrl', [
    'house', '$mdDialog', '$resources', '$scope', 'auth',
    function (house, $mdDialog, $resources, $scope, auth) {

      this.cancel = $mdDialog.cancel;
      
      if ('id' in house) {
        $scope.house = JSON.parse(JSON.stringify(house));
      } else {
        $scope.house = {
          'address': {
            'street': {},
            'house': {}
          }
        };
      }

      $scope.house.street_name = function (name) {
        if (arguments.length) {
          $scope.house.street = name;
          $scope.house.address.street.name = name;
        }
        return $scope.house.address.street.name;
      }

      $scope.house.house_number = function (number) {
        if (arguments.length) {
          $scope.house.number = number;
          $scope.house.address.house.number = number;
        }
        return $scope.house.address.house.number;
      }

      this.addHouse = function () {
        $scope.house['cooperative_id'] = house['associationId'];
        $scope.promise = $resources.assoc_houses.create(
          $scope.house,
          function (house) {
            $mdDialog.hide(house);
          }
        ).$promise;
      }

      this.saveHouse = function () {
        var deferred = $resources.houses.update({ id: house.id }, $scope.house);
        deferred.$promise.then(function (house) {
          $mdDialog.hide(house);
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'HouseDetailsCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', 'auth', '$routeParams', 'moment', '$mdEditDialog', 'breadcrumb',
   function ($mdDialog, $resources, $scope, $location, auth, $routeParams, moment, $mdEditDialog, breadcrumb) {

     breadcrumb.init($routeParams);

     $scope.indicatorsResource = $resources.house_indicators;
     $scope.indicatorsQueryParams = {
       house_id: $routeParams.houseId
     };

     $scope.chargesResource = $resources.house_charges;
     $scope.servicesResource = $resources.house_services;
     $scope.chargesQueryParams = {
       house_id: $routeParams.houseId
     };

     $scope.recalcChargesResource = $resources.house_recalccharges;
     $scope.recalcChargesCallback = function () {
       $scope.getAccounts();
     }

     var houseBlock = function (houseId) {
       $scope.housePromise = $resources.houses.get(
         { id: houseId },
         function (house) {
           $scope.house = house;
         }
       ).$promise;

       $scope.editHouse = function (event, house) {
         $mdDialog.show({
           clickOutsideToClose: true,
           controller: 'HouseModalCtrl',
           controllerAs: 'ctrl',
           focusOnOpen: true,
           targetEvent: event,
           locals: { house: house },
           templateUrl: 'house/house-dialog.html',
         }).then(function () {
           houseBlock(house.id);
         });
       };
     }

     var apartmentsBlock = function (houseId) {

       $scope.selectedApartments = [];

       $scope.filter = {
         options: {
           debounce: 500
         }
       };

       $scope.apartmentsQuery = {
         filter: '',
         limit: '5',
         order: 'address__apartment__number',
         page: 1
       };

       $scope.getApartments = function () {
         var query = $scope.apartmentsQuery;
         query['house_id'] = houseId;
         $scope.apartmentsPromise = $resources.house_apartments.get(
           $scope.apartmentsQuery,
           function (apartments) {
             $scope.apartments = apartments;
           }
         ).$promise;
       };

       $scope.getApartments();

       $scope.editApartment = function (event) {
         $mdDialog.show({
           clickOutsideToClose: true,
           controller: 'ApartmentDialogCtrl',
           controllerAs: 'ctrl',
           focusOnOpen: true,
           targetEvent: event,
           locals: { apartment: $scope.selectedApartments[0] },
           templateUrl: 'apartment/apartment-brief-dialog.html',
         }).then($scope.getApartments);
       };
     }

     var accountsBlock = function (houseId) {

       $scope.selectedAccounts = [];

       $scope.filter = {
         options: {
           debounce: 500
         }
       };

       $scope.accountsQuery = {
         filter: '',
         limit: '5',
         order: 'apartment__address__apartment__number',
         page: 1
       };

       $scope.getAccounts = function () {
         var query = $scope.accountsQuery;
         query['house_id'] = houseId;
         $scope.accountsPromise = $resources.house_accounts.get(
           query,
           function(accounts) {
             $scope.accounts = accounts;
           }).$promise;
       };

       $scope.getAccounts();

       $scope.editAccount = function (event, account) {
         if (!account) {
           account = $scope.selectedAccounts[0];
         }
         $mdDialog.show({
           clickOutsideToClose: true,
           controller: 'AccountDialogCtrl',
           controllerAs: 'ctrl',
           focusOnOpen: true,
           targetEvent: event,
           locals: { account: account },
           templateUrl: 'account/account-dialog.html',
         }).then($scope.getAccounts);
       };

       $scope.editFullname = function(event, account) {
         event.stopPropagation();

         $mdDialog.show({
           clickOutsideToClose: true,
           controller: 'AccountDialogCtrl',
           controllerAs: 'ctrl',
           focusOnOpen: true,
           targetEvent: event,
           locals: { account: account },
           templateUrl: 'account/edit-account-fullname-dialog.html',
         }).then(function () {
           $scope.getAccounts();
           $scope.getApartments();
         });
       }

       $scope.editBalance = function(event, account) {
         event.stopPropagation();

         $mdDialog.show({
           clickOutsideToClose: true,
           controller: 'AccountDialogCtrl',
           controllerAs: 'ctrl',
           focusOnOpen: true,
           targetEvent: event,
           locals: { account: account },
           templateUrl: 'account/edit-account-balance-dialog.html',
         }).then($scope.getAccounts);
       }
     }

     $scope.viewApartmentDetails = function (event, apartment) {
       event.stopPropagation();
       $location.path('/apartments/' + apartment.id + '/');
     }

     $scope.viewAccountDetails = function (event, apartment) {
       event.stopPropagation();
       $location.path('/apartments/' + apartment.id + '/account/');
     }

     var houseId = $routeParams.houseId;
     houseBlock(houseId);
     apartmentsBlock(houseId);
     accountsBlock(houseId);
   }]);

mod.controller(
  'HouseConfirmDialogCtrl',
  ['house', '$mdDialog', '$resources', '$scope', '$q',
    function (house, $mdDialog, $resources, $scope, $q) {

      self = this;

      this.cancel = $mdDialog.cancel;

      this.deleteHouse = function(house) {
        var deferred = $resources.houses.delete({ id: house.id });
        deferred.$promise.then(function () {
        });
        return deferred.$promise;
      }

      this.deletionConfirmed = function () {
        self.deleteHouse(house).then(function() {
          $mdDialog.hide();
        });
      }
    }]);

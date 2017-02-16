'use strict';

angular.module('myApp.house', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/associations/:cooperative_id/houses', {
      templateUrl: 'house/house.html',
      controller: 'HouseCtrl'
    });
    $routeProvider.when('/houses/:houseId', {
      templateUrl: 'house/house-details.html',
      controller: 'HouseDetailsCtrl'
    });
  }])

  .controller(
  'HouseCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', 'auth', '$routeParams',
    function ($mdDialog, $resources, $scope, $location, auth, $routeParams) {

      var self = this;

      var bookmark;

      var userInfo = auth.getUserInfo();
      var associationId = userInfo['cooperative_id'];

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

      $scope.viewApartments = function (event, house_id) {
        $location.url('/houses/' + house_id + '/apartments/');
      }

      $scope.addHouse = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddHouseController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'house/add-house-dialog.html',
        }).then($scope.getHouses);
      };

      $scope.deleteHouse = function (event) {
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

      $scope.editHouse = function (event) {
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

      function success(houses) {
        $scope.houses = houses;
      }

      $scope.getHouses = function () {
        var query = $scope.query;
        if ($routeParams.cooperative_id !== undefined) {
          query['cooperative_id'] = $routeParams.cooperative_id;
          $scope.promise = $resources.assoc_houses.get(
            $scope.query, success).$promise;
        } else if (associationId) {
          query['cooperative_id'] = associationId;
          $scope.promise = $resources.assoc_houses.get(
            $scope.query, success).$promise;
        } else {
          $scope.promise = $resources.houses.get(
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

        $scope.getHouses();
      });

    }])

  .controller(
  'AddHouseController', [
    '$mdDialog', '$resources', '$scope', 'auth',
    function ($mdDialog, $resources, $scope, auth) {

      var self = this;

      this.add = true;

      this.cancel = $mdDialog.cancel;

      var userInfo = auth.getUserInfo();
      self.associationId = userInfo['cooperative_id'];

      $scope.house = {};

      $scope.house.street_name = function (name) {
        if (arguments.length) {
          $scope.house.street = name;
        }
        return $scope.house.street;
      }

      $scope.house.house_number = function (number) {
        if (arguments.length) {
          $scope.house.number = number;
        }
        return $scope.house.number;
      }

      function success(house) {
        $mdDialog.hide(house);
      }

      this.addHouse = function () {
        var data = {
          cooperative_id: self.associationId
        }
        $scope.house['cooperative_id'] = self.associationId;
        $scope.promise = $resources.assoc_houses.create($scope.house, success).$promise;
      }
    }])

  .controller('DeleteHouseController',
  ['houses', '$mdDialog', '$resources', '$scope', '$q',
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

    }])

  .controller('EditHouseController',
  ['house', '$mdDialog', '$resources', '$scope', '$q',
    function (house, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.house = JSON.parse(JSON.stringify(house));

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

      this.updateHouse = function () {
        var deferred = $resources.houses.update({ id: house.id }, $scope.house);
        deferred.$promise.then(function () {
          $mdDialog.hide(house);
        });
        return deferred.$promise;
      }

    }])

  .controller(
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
    }])

  .controller(
    'HouseDetailsCtrl',
    ['$mdDialog', '$resources', '$scope', '$location', 'auth', '$routeParams', 'moment', '$mdEditDialog', 'breadcrumb',
     function ($mdDialog, $resources, $scope, $location, auth, $routeParams, moment, $mdEditDialog, breadcrumb) {

       breadcrumb.init($routeParams);

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
           order: 'id',
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
             templateUrl: 'apartment/apartment-dialog.html',
           }).then($scope.getApartments);
         };

         $scope.viewApartmentDetails = function (event, apartment) {
           event.stopPropagation();
           $location.path('/apartments/' + apartment.id + '/');
         }
       }

       var indicatorsBlock = function(houseId) {

         $scope.selectedIndicators = [];

         $scope.filter = {
           options: {
             debounce: 500
           }
         };

         $scope.indicatorsQuery = {
           filter: '',
           limit: '5',
           order: 'id',
           page: 1,
           period: new Date(moment({ day: 1 }).format("YYYY-MM-DD")),
         };

         $scope.getIndicators = function () {
           var query = $scope.indicatorsQuery;
           query['house_id'] = houseId;
           $scope.indicatorsPromise = $resources.house_indicators.get(
             query,
             function (indicators) {
               $scope.indicators = indicators;
             }
           ).$promise;
         };

         $scope.$watch(
           'indicatorsQuery.period',
           function (newValue, oldValue) {
             $scope.getIndicators();
           }
         );

         $scope.editIndicator = function (event) {
           $mdDialog.show({
             clickOutsideToClose: true,
             controller: 'IndicatorDialogCtrl',
             controllerAs: 'ctrl',
             focusOnOpen: true,
             targetEvent: event,
             locals: { indicator: $scope.selectedIndicators[0] },
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
               function(indicator) {
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
           order: 'last_name',
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

         $scope.editAccount = function (event) {
           $mdDialog.show({
             clickOutsideToClose: true,
             controller: 'AccountDialogCtrl',
             controllerAs: 'ctrl',
             focusOnOpen: true,
             targetEvent: event,
             locals: { account: $scope.selectedAccounts[0] },
             templateUrl: 'account/account-dialog.html',
           }).then($scope.getAccounts);
         };

         $scope.viewApartmentDetails = function (event, apartment) {
           event.stopPropagation();
           $location.path('/apartments/' + apartment.id + '/');
         }

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
           }).then($scope.getAccounts);
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

       var houseId = $routeParams.houseId;
       houseBlock(houseId);
       apartmentsBlock(houseId);
       indicatorsBlock(houseId);
       accountsBlock(houseId);

     }])

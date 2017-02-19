'use strict';

var mod = angular.module('myApp.association', ['ngRoute']);

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/associations/:association_id/', {
    templateUrl: 'association/association-details.html',
    controller: 'AssociationDetailsCtrl'
  });
}]);

mod.controller(
  'AssociationDetailsCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', '$routeParams', 'breadcrumb',
    function ($mdDialog, $resources, $scope, $location, $routeParams, breadcrumb) {

      breadcrumb.init($routeParams);

      this.cancel = $mdDialog.cancel;

      var housesBlock = function (associationId) {

        $scope.selectedHouses = [];

        $scope.houseQuery = {
          filter: '',
          limit: '5',
          order: 'id',
          page: 1
        };

        $scope.getHouses = function () {
          var query = $scope.houseQuery;
          query['cooperative_id'] = associationId;
          $scope.housesPromise = $resources.assoc_houses.get(
            query,
            function (houses) {
              $scope.houses = houses;
            }
          ).$promise;
        };

        $scope.getHouses();

        $scope.addHouse = function (event) {
          var house = {
            'associationId': associationId
          };
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'HouseModalCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { house: house },
            templateUrl: 'house/house-dialog.html',
          }).then($scope.getHouses);
        };

        $scope.deleteHouse = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'HouseConfirmDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: false,
            targetEvent: event,
            locals: { house: $scope.selectedHouses[0] },
            templateUrl: 'house/delete-dialog.html',
          }).then(function () {
            $scope.getHouses();
            $scope.selectedHouses = [];
          });
        };

        $scope.viewHouseDetails = function (event, house) {
          event.stopPropagation();
          $location.path('/houses/' + house.id + '/');
        };
      }

      var associationBlock = function (associationId) {
        $scope.cooperatives_promise = $resources.associations.get(
          { id: associationId },
          function (association) {
            $scope.association = association;
          }
        ).$promise;
      }

      var servicesBlock = function (associationId) {

        function services_succcess(services) {
          $scope.services = services;
        }

        $scope.getAssocServices = function () {
          $scope.servicesPromise = $resources.assoc_services.get(
            { cooperative_id: associationId, limit: 50 }, services_succcess).$promise;
        }
        $scope.getAssocServices();

        $scope.changeInformation = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ChangeInformationController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { association: $scope.association },
            templateUrl: 'association/change-association-dialog.html',
          }).then($scope.getAssociations);
        };

        $scope.changeServices = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ChangeAssociationServicesController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: {
              association: $scope.association,
              assoc_services: $scope.services.data
            },
            templateUrl: 'association/change-association-services-dialog.html',
          }).then(function () {
            $scope.getAssocServices();
          });
        }
      }

      var bankAccountsBlock = function (associationId) {

        $scope.selectedBankAccounts = [];

        $scope.bankAccountsQuery = {
          filter: '',
          limit: '5',
          order: 'name',
          page: 1
        };

        $scope.getBankAccounts = function () {
          var query = $scope.bankAccountsQuery;
          query['cooperative_id'] = associationId;
          $scope.bankAccountsPromise = $resources.assoc_bank_accounts.get(
            query,
            function (bankAccounts) {
              $scope.bankAccounts = bankAccounts;
            }
          ).$promise;
        };

        $scope.getBankAccounts();

        $scope.addBankAccount = function (event) {
          var bankAccount = {
            'associationId': associationId
          };
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'BankAccountDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { bankAccount: bankAccount },
            templateUrl: 'bank-account/bank-account-dialog.html',
          }).then($scope.getBankAccounts);
        };

        $scope.editBankAccount = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'BankAccountDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { bankAccount: $scope.selectedBankAccounts[0] },
            templateUrl: 'bank-account/bank-account-dialog.html',
          }).then($scope.getBankAccounts);
        }

        $scope.deleteBankAccount = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'BankAccountConfirmDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: false,
            targetEvent: event,
            locals: { bankAccount: $scope.selectedBankAccounts[0] },
            templateUrl: 'bank-account/delete-dialog.html',
          }).then(function () {
            $scope.getBankAccounts();
            $scope.selectedBankAccounts = [];
          });
        };
      }

      var associationId = $routeParams.association_id;

      housesBlock(associationId);
      associationBlock(associationId);
      servicesBlock(associationId);
      bankAccountsBlock(associationId);
    }]);

mod.controller(
  'ChangeInformationController',
  ['association', '$scope', '$mdDialog', '$resources',
    function (association, $scope, $mdDialog, $resources) {

      $scope.association = association;

      this.cancel = $mdDialog.cancel;

      this.saveAssociation = function (event) {

        var deferred = $resources.cooperatives.update(
          {
            id: association.id
          },
          $scope.association
        );
        deferred.$promise.then(function () {
          $mdDialog.hide();
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'ChangeAssociationServicesController',
  ['association', 'assoc_services', '$scope', '$mdDialog', '$resources',
    function (association, assoc_services, $scope, $mdDialog, $resources) {

      $scope.selected = [];

      $scope.association = association;

      // The services which are assigned to the association.
      $scope.assoc_services = assoc_services;

      this.cancel = $mdDialog.cancel;

      var services_success = function (services) {
        $scope.services = services.data;
        var selected_service_ids = [];
        for (var i = 0; i < assoc_services.length; i++) {
          var assoc_service = assoc_services[i];
          selected_service_ids.push(assoc_service.service.id);
        }
        for (var i = 0; i < $scope.services.length; i++) {
          var service = $scope.services[i];
          if (selected_service_ids.indexOf(service.id) !== -1) {
            $scope.services[i].selected = true;
          }
        }
      };

      $resources.services.get({ 'limit': 50 }, services_success).$promise;

      this.saveAssociationServices = function (event) {

        var selected_service_ids = [];
        for (var i = 0; i < $scope.services.length; i++) {
          var service = $scope.services[i];
          if (service.selected) {
            selected_service_ids.push(service.id);
          }
        }
        var deferred = $resources.cooperative_services.update(
          {
            cooperative_id: $scope.association.id
          },
          selected_service_ids
        );
        deferred.$promise.then(function () {
          $mdDialog.hide();
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'AssociationDialogCtrl',
  ['$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      this.addAssociation = function () {
        $scope.promise = $resources.associations.create(
          $scope.association,
          function (association) {
            $mdDialog.hide(association);
          }
        ).$promise;
      }

    }]);

mod.controller(
  'AssociationConfirmDialogCtrl',
  ['associations', '$mdDialog', '$resources', '$scope', '$q',
    function (associations, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(associations.forEach(deleteAssociation)).then(onComplete);
      }

      function deleteAssociation(association, index) {
        var deferred = $resources.associations.delete({ id: association.id });
        deferred.$promise.then(function () {
          associations.splice(index, 1);
        });
        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }
    }]);

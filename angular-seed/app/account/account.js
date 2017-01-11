'use strict';

angular.module('myApp.account', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/apartment/:id/account', {
      templateUrl: 'account/account.html',
      controller: 'AccountCtrl'
    });
    $routeProvider.when('/accounts', {
      templateUrl: 'account/account.html',
      controller: 'AccountCtrl'
    });
  }])

  .controller(
  'AccountCtrl',
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
        order: 'first_name',
        page: 1
      };

      $scope.addAccount = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddAccountController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'account/add-account-dialog.html',
        }).then($scope.getAccounts);
      };

      $scope.deleteAccount = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteAccountController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { apartments: $scope.selected },
          templateUrl: 'account/delete-dialog.html',
        }).then($scope.getAccounts);
      };

      $scope.editAccount = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditAccountController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { account: $scope.selected[0] },
            templateUrl: 'account/add-account-dialog.html',
          }).then($scope.getAccounts);
        }
      };

      function success(accounts) {
        $scope.accounts = accounts;
      }

      $scope.getAccounts = function () {
        var query = $scope.query;
        if ($routeParams.id !== undefined) {
          query['apartment_id'] = $routeParams.id;
          $scope.promise = $resources.apartment_owner.get(
            $scope.query, success).$promise;
        } else {
          $scope.promise = $resources.accounts.get(
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

        $scope.getAccounts();
      });

    }])

  .controller('AddAccountController',
  ['$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(account) {
        $mdDialog.hide(account);
      }

      this.saveAccount = function () {
        $scope.promise = $resources.apartment_owner.create(
          $scope.apartment, success).$promise;
      }
    }])

  .controller('DeleteAccountController',
  ['accounts', '$mdDialog', '$resources', '$scope', '$q',
    function (accounts, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(accounts.forEach(deleteAccount)).then(onComplete);
      }

      function deleteAccount(account, index) {
        var deferred = $resources.apartments.delete({ id: account.id });

        deferred.$promise.then(function () {
          account.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }])

  .controller('EditAccountController',
  ['account', '$mdDialog', '$resources', '$scope', '$q',
    function (account, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.account = JSON.parse(JSON.stringify(account));

      this.updateAccount = function () {
        var deferred = $resources.accounts.update({ id: account.id }, $scope.account);
        deferred.$promise.then(function () {
          $mdDialog.hide(account);
        });
        return deferred.$promise;
      }

    }]);

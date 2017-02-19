'use strict';

var mod = angular.module('myApp.bankAccount', ['ngRoute']);

mod.controller(
  'BankAccountDialogCtrl',
  ['bankAccount', '$mdDialog', '$resources', '$scope',
    function (bankAccount, $mdDialog, $resources, $scope) {

      this.cancel = $mdDialog.cancel;

      $scope.bankAccount = JSON.parse(JSON.stringify(bankAccount));

      this.saveBankAccount = function () {
        var deferred = $resources.bank_accounts.update({ id: bankAccount.id }, $scope.bankAccount);
        deferred.$promise.then(function (response) {
          $mdDialog.hide(response);
        });
        return deferred.$promise;
      }

      this.addBankAccount = function () {
        $scope.bankAccount['cooperative_id'] = bankAccount['associationId'];
        $scope.promise = $resources.assoc_bank_accounts.create(
          $scope.bankAccount,
          function (bankAccount) {
            $mdDialog.hide(bankAccount);
          }
        ).$promise;
      }
    }]);

mod.controller(
  'BankAccountConfirmDialogCtrl',
  ['bankAccount', '$mdDialog', '$resources', '$scope', '$q',
    function (bankAccount, $mdDialog, $resources, $scope, $q) {

      self = this;

      this.cancel = $mdDialog.cancel;

      this.deleteBankAccount = function (bankAccount) {
        var deferred = $resources.bank_accounts.delete({ id: bankAccount.id });
        deferred.$promise.then(function () {
        });
        return deferred.$promise;
      }

      this.deletionConfirmed = function () {
        self.deleteBankAccount(bankAccount).then(function () {
          $mdDialog.hide();
        });
      }
    }]);

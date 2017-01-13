'use strict';

angular.module('myApp.navbar', ['ngRoute'])

  .controller(
  'NavbarCtrl',
  ['$scope', '$location', 'auth',
    function ($scope, $location, auth) {

      var userInfo = auth.getUserInfo();
      $scope.associationName = userInfo['cooperative_name'];

      this.gotoAssociations = function () {
        $location.url('/');
      }

      this.gotoHouses = function () {
        $location.url('houses');
      }

      this.gotoApartments = function () {
        $location.url('apartments');
      }

      this.gotoAccounts = function () {
        $location.url('accounts');
      }

      this.gotoCharges = function () {
        $location.url('charges');
      }

      this.gotoServices = function () {
        $location.url('services');
      }

    }]);
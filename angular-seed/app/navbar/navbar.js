'use strict';

var mod = angular.module('myApp.navbar', ['ngRoute'])

mod.controller(
  'NavbarCtrl',
  ['$scope', '$location', 'auth',
    function ($scope, $location, auth) {

      $scope.showAssociationName = function () {
        return auth.isAuthed() && $scope.associationName;
      }

      $scope.showAdmin = function () {
        return auth.isAuthed() && $scope.isSuperAdmin == true;
      }

      $scope.showMenu = function () {
        return false;
        return auth.isAuthed();
      }

      var userInfo = auth.getUserInfo();
      if (userInfo) {
        $scope.associationName = userInfo['cooperative_name'];
        $scope.isSuperAdmin = userInfo['superuser'];
      }

      this.isSuperAdmin = function () {
        return $scope.isSuperAdmin;
      }

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

      this.gotoLogin = function () {
        $location.url('login');
      }

      this.gotoMeters = function () {
        $location.url('meters');
      }

      this.gotoIndicators = function () {
        $location.url('indicators');
      }
    }]);

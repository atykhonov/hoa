'use strict';

angular.module('myApp.navbar', ['ngRoute'])

  .controller('NavbarCtrl', ['$scope', '$location', function ($scope, $location) {

    this.gotoAssociations = function () {
      $location.url('associations');
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

    this.gotoServices = function () {
      $location.url('services');
    }

  }]);

'use strict';

angular.module('myApp.navbar', ['ngRoute'])

  .controller('NavbarCtrl', ['$scope', '$location', function ($scope, $location) {

    this.currentNavItem = 'associations';

    this.gotoAssociations = function () {
      $location.url('associations');
    }

    this.gotoHouses = function () {
      $location.url('houses');
    }

    this.gotoApartments = function () {
      $location.url('apartments');
    }

  }]);

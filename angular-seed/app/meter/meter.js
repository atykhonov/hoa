'use strict';

var app = angular.module('myApp.meter', ['ngRoute']);

app.config([
  '$routeProvider',
  function ($routeProvider) {
    $routeProvider.when('/meters', {
      templateUrl: 'meter/meter.html',
      controller: 'MeterCtrl'
    });
  }]);

app.controller(
  'MeterCtrl', [
    '$mdDialog', '$resources', '$scope', '$location', 'auth',
    function ($mdDialog, $resources, $scope, $location, auth) {

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
        order: 'name',
        page: 1
      };

      $scope.viewApartments = function (event, house_id) {
        $location.url('/houses/' + house_id + '/apartments/');
      }

      $scope.addMeter = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddHouseController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'house/add-house-dialog.html',
        }).then($scope.getHouses);
      };

      $scope.deleteMeter = function (event) {
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

      $scope.editMeter = function (event) {
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
        query['cooperative_id'] = associationId;
        $scope.promise = $resources.assoc_houses.get(
          $scope.query, success).$promise;
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

    }]);

app.controller(
  'AddMeterController', [
    '$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(house) {
        $mdDialog.hide(house);
      }

      this.addHouse = function () {
        $scope.house['cooperative_id'] = associationId;
        $scope.promise = $resources.assoc_houses.create($scope.house, success).$promise;
      }
    }])

app.controller(
  'DeleteMeterController', [
    'houses', '$mdDialog', '$resources', '$scope', '$q',
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

    }]);

app.controller(
  'EditMeterController', [
    'house', '$mdDialog', '$resources', '$scope', '$q',
    function (house, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.house = JSON.parse(JSON.stringify(house));

      this.updateHouse = function () {
        var deferred = $resources.houses.update({ id: house.id }, $scope.house);
        deferred.$promise.then(function () {
          $mdDialog.hide(house);
        });
        return deferred.$promise;
      }

    }]);

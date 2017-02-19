'use strict';

var mod = angular.module('myApp.service', ['ngRoute'])

mod.controller(
  'ServiceDialogCtrl',
  ['service', '$mdDialog', '$resources', '$scope', '$q',
    function (service, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.service = JSON.parse(JSON.stringify(service));

      function units_success(units) {
        $scope.units = units.data;
      }

      $scope.promise = $resources.units.get(
        $scope.query, units_success).$promise;

      this.saveService = function () {
        var deferred = $resources.services.update({ id: service.id }, $scope.service);
        deferred.$promise.then(function (service) {
          $mdDialog.hide(service);
        });
        return deferred.$promise;
      }

    }]);

mod.controller(
  'AssignServiceController',
  ['cooperative_id', '$mdDialog', '$resources', '$scope', '$q',
    function (cooperative_id, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      function services_success(services) {
        $scope.services = services.data;
      }

      $scope.promise = $resources.services.get(
        $scope.query, services_success).$promise;

      function success(service) {
        $mdDialog.hide(service);
      }

      function error(message) {
        $scope.error = message.data;
      }

      this.assignService = function () {
        $scope.service['cooperative_id'] = cooperative_id;
        $resources.cooperative_services.create($scope.service, success, error);
      }

    }]);

mod.controller(
  'UnassignServiceController',
  ['services', 'cooperative_id', '$mdDialog', '$resources', '$scope', '$q',
    function (services, cooperative_id, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(services.forEach(unassignService)).then(onComplete);
      }

      function unassignService(service, index) {

        var deferred = $resources.cooperative_services.delete({
          service_id: service.id,
          cooperative_id: cooperative_id
        });

        deferred.$promise.then(function () {
          services.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }]);

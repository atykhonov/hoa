'use strict';

angular.module('myApp.service', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/cooperative/:cooperative_id/services/', {
      templateUrl: 'service/cooperative-service.html',
      controller: 'ServiceCtrl'
    });
    $routeProvider.when('/services', {
      templateUrl: 'service/service.html',
      controller: 'ServiceCtrl'
    });
  }])

  .controller(
  'ServiceCtrl',
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
        order: 'id',
        page: 1
      };

      $scope.addService = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddServiceController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'service/add-service-dialog.html',
        }).then($scope.getServices);
      };

      $scope.assignService = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AssignServiceController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: { cooperative_id: $routeParams.cooperative_id },
          templateUrl: 'service/assign-service-dialog.html',
        }).then($scope.getServices);
      };

      $scope.unassignService = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'UnassignServiceController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: {
            services: $scope.selected,
            cooperative_id: $routeParams.cooperative_id
          },
          templateUrl: 'service/delete-dialog.html',
        }).then($scope.getServices);
      };

      $scope.deleteService = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteServiceController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { services: $scope.selected },
          templateUrl: 'service/delete-dialog.html',
        }).then($scope.getServices);
      };

      $scope.editService = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditServiceController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { service: $scope.selected[0] },
            templateUrl: 'service/add-service-dialog.html',
          }).then($scope.getServices);
        }
      };

      function success(services) {
        $scope.services = services;
      }

      $scope.getServices = function () {
        var query = $scope.query;
        if ($routeParams.cooperative_id !== undefined) {
          query['cooperative_id'] = $routeParams.cooperative_id;
          $scope.promise = $resources.cooperative_services.get(
            $scope.query, success).$promise;
        } else {
          $scope.promise = $resources.services.get(
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

        $scope.getServices();
      });

    }])

  .controller(
  'AddServiceController',
  ['$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function units_success(units) {
        $scope.units = units.data;
      }

      $scope.promise = $resources.units.get(
        $scope.query, units_success).$promise;

      function servicesSuccess(services) {
        $scope.services = services;
      }

      $scope.promise = $resources.services.get(
        $scope.query, servicesSuccess).$promise;

      function success(service) {
        $mdDialog.hide(service);
      }

      this.saveService = function () {
        $scope.promise = $resources.services.create(
          $scope.service, success).$promise;
      }
    }])

  .controller('DeleteServiceController',
  ['services', '$mdDialog', '$resources', '$scope', '$q',
    function (services, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(services.forEach(deleteService)).then(onComplete);
      }

      function deleteService(service, index) {
        var deferred = $resources.services.delete({ id: service.id });

        deferred.$promise.then(function () {
          services.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }])

  .controller('EditServiceController',
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
        deferred.$promise.then(function () {
          $mdDialog.hide(service);
        });
        return deferred.$promise;
      }

    }])

  .controller('AssignServiceController',
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

    }])

  .controller(
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

    }])
  ;

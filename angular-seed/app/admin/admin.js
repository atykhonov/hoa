var mod = angular.module('myApp.admin', ['ngRoute']);

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/admin', {
    controller: 'AdminCtrl',
    templateUrl: 'admin/admin.html'
  });
}]);

mod.controller(
  'AdminCtrl',
  ['$scope', '$location', '$resources', '$mdDialog', 'auth', 'breadcrumb',
    function ($scope, $location, $resources, $mdDialog, auth, breadcrumb) {

      breadcrumb.init({});

      var associationsBlock = function () {

        $scope.selectedAssociations = [];

        $scope.associationQuery = {
          filter: '',
          limit: '5',
          order: 'name',
          page: 1
        };

        $scope.getAssociations = function () {
          $scope.associationsPromise = $resources.associations.get(
            $scope.associationQuery,
            function (associations) {
              $scope.associations = associations;
            }
          ).$promise;
        };

        $scope.getAssociations();

        $scope.addAssociation = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'AssociationDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            templateUrl: 'association/add-association-dialog.html',
          }).then($scope.getAssociations);
        };

        $scope.deleteAssociation = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'AssociationConfirmDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: false,
            targetEvent: event,
            locals: { associations: $scope.selectedAssociations },
            templateUrl: 'association/delete-dialog.html',
          }).then($scope.getAssociations);
        };

        $scope.viewAssociationDetails = function (event, association) {
          event.stopPropagation();
          $location.path('/associations/' + association.id + '/');
        };
      };

      var usersBlock = function () {

        $scope.selectedUsers = [];

        $scope.userQuery = {
          filter: '',
          limit: '5',
          order: 'email',
          page: 1
        };

        $scope.getUsers = function () {
          $scope.usersPromise = $resources.users.get(
            $scope.userQuery,
            function (users) {
              $scope.users = users;
            }
          ).$promise;
        };

        $scope.getUsers();

        $scope.addUser = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'UserDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { associations: $scope.associations },
            templateUrl: 'user/user-dialog.html',
          }).then($scope.getUsers);
        };

        $scope.deleteUser = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'UserConfirmDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: false,
            targetEvent: event,
            locals: { users: $scope.selectedUsers },
            templateUrl: 'user/delete-dialog.html',
          }).then($scope.getUsers);
        };
      };

      var servicesBlock = function () {

        $scope.selectedServices = [];

        $scope.serviceQuery = {
          filter: '',
          limit: '5',
          order: 'name',
          page: 1
        };

        $scope.getServices = function () {
          $scope.servicesPromise = $resources.services.get(
            $scope.serviceQuery,
            function (services) {
              $scope.services = services;
            }
          ).$promise;
        };

        $scope.editService = function (event) {
          event.stopPropagation();
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ServiceDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { service: $scope.selectedServices[0] },
            templateUrl: 'service/service-dialog.html',
          }).then($scope.getServices);
        }

        $scope.getServices();
      };

      associationsBlock();
      usersBlock();
      servicesBlock();

    }]);

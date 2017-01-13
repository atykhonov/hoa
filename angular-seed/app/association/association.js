'use strict';

angular.module('myApp.association', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'association/association-manager.html',
      controller: 'AssociationManagerCtrl'
    });
    $routeProvider.when('/associations/', {
      templateUrl: 'association/association.html',
      controller: 'AssociationCtrl'
    });
    $routeProvider.when('/associations/:id/', {
      templateUrl: 'association/association-details.html',
      controller: 'AssociationDetailsCtrl'
    });
  }])

  .controller(
  'AssociationCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', '$rootScope',
    function ($mdDialog, $resources, $scope, $location, $rootScope) {

      console.log('Association ID: ');
      console.log($rootScope.associationId);

      $scope.test = 'best';

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
        order: 'name',
        page: 1
      };

      $scope.editServices = function (event, association_id) {
        $location.url('/cooperative/' + association_id + '/services/');
      }

      $scope.viewHouses = function (event, association_id) {
        $location.url('/associations/' + association_id + '/houses/');
      }

      $scope.addAssociation = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddAssociationController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'association/add-association-dialog.html',
        }).then($scope.getAssociations);
      };

      $scope.deleteAssociation = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteAssociationController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { associations: $scope.selected },
          templateUrl: 'association/delete-dialog.html',
        }).then($scope.getAssociations);
      };

      $scope.editAssociation = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { association: $scope.selected[0] },
            templateUrl: 'association/add-association-dialog.html',
          }).then($scope.getAssociations);
        }
      };

      function success(associations) {
        $scope.associations = associations;
      }

      $scope.getAssociations = function () {
        $scope.promise = $resources.cooperatives.get($scope.query, success).$promise;
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

        $scope.getAssociations();
      });

    }])

  .controller('AddAssociationController',
  ['$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(association) {
        $mdDialog.hide(association);
      }

      this.addAssociation = function () {
        $scope.promise = $resources.cooperatives.create($scope.association, success).$promise;
      }

    }])

  .controller('DeleteAssociationController',
  ['associations', '$mdDialog', '$resources', '$scope', '$q',
    function (associations, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(associations.forEach(deleteAssociation)).then(onComplete);
      }

      function deleteAssociation(association, index) {
        var deferred = $resources.cooperatives.delete({ id: association.id });

        deferred.$promise.then(function () {
          associations.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }])

  .controller('EditController',
  ['association', '$mdDialog', '$resources', '$scope', '$q',
    function (association, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.association = JSON.parse(JSON.stringify(association));

      this.updateAssociation = function () {
        var deferred = $resources.cooperatives.update({ id: association.id }, $scope.association);
        deferred.$promise.then(function () {
          $mdDialog.hide(association);
        });
        return deferred.$promise;
      }

    }])

  .controller(
  'AssociationDetailsCtrl',
  ['$mdDialog', '$resources', '$scope', '$location',
    function ($mdDialog, $resources, $scope, $location) {
    }])

  .controller(
  'AssociationManagerCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', 'auth',
    function ($mdDialog, $resources, $scope, $location, auth) {

      $scope.selected = [];

      var userInfo = auth.getUserInfo();
      var associationId = userInfo['cooperative_id'];

      function cooperatives_success(association) {
        $scope.association = association;
      }

      function services_succcess(services) {
        $scope.services = services;
      }

      $scope.cooperatives_promise = $resources.cooperatives.get(
        { id: associationId }, cooperatives_success).$promise;

      $scope.services_promise = $resources.cooperative_services.get(
        { cooperative_id: associationId }, services_succcess).$promise;
    }]);

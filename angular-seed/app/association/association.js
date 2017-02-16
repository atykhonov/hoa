'use strict';

var mod = angular.module('myApp.association', ['ngRoute']);

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/associations/', {
    templateUrl: 'association/association.html',
    controller: 'AssociationCtrl'
  });
  $routeProvider.when('/associations/:association_id/', {
    templateUrl: 'association/association-details.html',
    controller: 'AssociationDetailsCtrl'
  });
}]);

mod.controller(
  'AssociationCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', '$rootScope',
    function ($mdDialog, $resources, $scope, $location, $rootScope) {

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

    }]);

mod.controller(
  'AddAssociationController',
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

    }]);

mod.controller(
  'DeleteAssociationController',
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

    }]);

mod.controller(
  'EditController',
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

    }]);

mod.controller(
  'AssociationDetailsCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', '$routeParams', 'breadcrumb',
    function ($mdDialog, $resources, $scope, $location, $routeParams, breadcrumb) {

      // var params = {
      //   association_id: $routeParams.association_id
      // };

      breadcrumb.init($routeParams);

      this.cancel = $mdDialog.cancel;

      var housesBlock = function (associationId) {

        $scope.selectedHouses = [];

        $scope.houseQuery = {
          filter: '',
          limit: '5',
          order: 'id',
          page: 1
        };

        $scope.getHouses = function () {
          $scope.housesPromise = $resources.houses.get(
            $scope.query,
            function (houses) {
              $scope.houses = houses;
            }
          ).$promise;
        };

        $scope.getHouses();

        $scope.addHouse = function (event) {
          var house = {
            'associationId': associationId
          };
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'HouseModalCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { house: house },
            templateUrl: 'house/house-dialog.html',
          }).then($scope.getHouses);
        };

        $scope.viewHouseDetails = function (event, house) {
          event.stopPropagation();
          $location.path('/houses/' + house.id + '/');
        };
      }

      var associationBlock = function (associationId) {
        $scope.cooperatives_promise = $resources.associations.get(
          { id: associationId },
          function (association) {
            $scope.association = association;
          }
        ).$promise;
      }

      var servicesBlock = function (associationId) {

        function services_succcess(services) {
          $scope.services = services;
        }

        $scope.getAssocServices = function () {
          $scope.services_promise = $resources.assoc_services.get(
            { cooperative_id: associationId, limit: 50 }, services_succcess).$promise;
        }
        $scope.getAssocServices();

        $scope.changeInformation = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ChangeInformationController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { association: $scope.association },
            templateUrl: 'association/change-association-dialog.html',
          }).then($scope.getAssociations);
        };

        $scope.changeServices = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ChangeAssociationServicesController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: {
              association: $scope.association,
              assoc_services: $scope.services.data
            },
            templateUrl: 'association/change-association-services-dialog.html',
          }).then(function () {
            $scope.getAssocServices();
          });
        }
      }

      var associationId = $routeParams.association_id;
      housesBlock(associationId);
      associationBlock(associationId);
      servicesBlock(associationId);
    }]);

mod.controller(
  'ChangeInformationController',
  ['association', '$scope', '$mdDialog', '$resources',
    function (association, $scope, $mdDialog, $resources) {

      $scope.association = association;

      this.cancel = $mdDialog.cancel;

      this.saveAssociation = function (event) {

        var deferred = $resources.cooperatives.update(
          {
            id: association.id
          },
          $scope.association
        );
        deferred.$promise.then(function () {
          $mdDialog.hide();
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'ChangeAssociationServicesController',
  ['association', 'assoc_services', '$scope', '$mdDialog', '$resources',
    function (association, assoc_services, $scope, $mdDialog, $resources) {

      $scope.selected = [];

      $scope.association = association;

      // The services which are assigned to the association.
      $scope.assoc_services = assoc_services;

      this.cancel = $mdDialog.cancel;

      var services_success = function (services) {
        $scope.services = services.data;
        var selected_service_ids = [];
        for (var i = 0; i < assoc_services.length; i++) {
          var assoc_service = assoc_services[i];
          selected_service_ids.push(assoc_service.service.id);
        }
        for (var i = 0; i < $scope.services.length; i++) {
          var service = $scope.services[i];
          if (selected_service_ids.indexOf(service.id) !== -1) {
            $scope.services[i].selected = true;
          }
        }
      };

      $resources.services.get({ 'limit': 50 }, services_success).$promise;

      this.saveAssociationServices = function (event) {

        var selected_service_ids = [];
        for (var i = 0; i < $scope.services.length; i++) {
          var service = $scope.services[i];
          if (service.selected) {
            selected_service_ids.push(service.id);
          }
        }
        var deferred = $resources.cooperative_services.update(
          {
            cooperative_id: $scope.association.id
          },
          selected_service_ids
        );
        deferred.$promise.then(function () {
          $mdDialog.hide();
        });
        return deferred.$promise;
      }
    }]);

mod.controller(
  'AssociationManagerCtrl',
  ['$mdDialog', '$resources', '$scope', '$location', 'auth',
    function ($mdDialog, $resources, $scope, $location, auth) {

      this.cancel = $mdDialog.cancel;

      var userInfo = auth.getUserInfo();
      if (userInfo === undefined) {
        $location.path('/login');
      }
      if (userInfo['is_superuser']) {
        $location.path('/associations');
        return;
      }
      var associationId = userInfo['cooperative_id'];

      function cooperatives_success(association) {
        $scope.association = association;
      }

      function services_succcess(services) {
        $scope.services = services;
      }

      $scope.cooperatives_promise = $resources.cooperatives.get(
        { id: associationId }, cooperatives_success).$promise;

      $scope.getAssocServices = function () {
        $scope.services_promise = $resources.cooperative_services.get(
          { cooperative_id: associationId, limit: 50 }, services_succcess).$promise;
      }
      $scope.getAssocServices();

      $scope.changeInformation = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'ChangeInformationController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: { association: $scope.association },
          templateUrl: 'association/change-association-dialog.html',
        }).then($scope.getAssociations);
      };

      $scope.changeServices = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'ChangeAssociationServicesController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: {
            association: $scope.association,
            assoc_services: $scope.services.data
          },
          templateUrl: 'association/change-association-services-dialog.html',
        }).then(function () {
          $scope.getAssocServices();
        });
      }
    }]);

mod.controller(
  'AssociationDialogCtrl',
  ['$mdDialog', '$resources', '$scope',
    function ($mdDialog, $resources, $scope) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      this.addAssociation = function () {
        $scope.promise = $resources.associations.create(
          $scope.association,
          function (association) {
            $mdDialog.hide(association);
          }
        ).$promise;
      }

    }]);

mod.controller(
  'AssociationConfirmDialogController',
  ['associations', '$mdDialog', '$resources', '$scope', '$q',
    function (associations, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(associations.forEach(deleteAssociation)).then(onComplete);
      }

      function deleteAssociation(association, index) {
        var deferred = $resources.associations.delete({ id: association.id });
        deferred.$promise.then(function () {
          associations.splice(index, 1);
        });
        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }
    }]);

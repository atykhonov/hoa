'use strict';

angular.module('myApp.mdtable', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/mdtable', {
      templateUrl: 'mdtable/mdtable.html',
      controller: 'MdTableCtrl'
    });
  }])

  .controller('MdTableCtrl', ['$mdDialog', '$nutrition', '$scope', function ($mdDialog, $nutrition, $scope) {

    'use strict';

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

    $scope.addItem = function (event) {
      $mdDialog.show({
        clickOutsideToClose: true,
        controller: 'addItemController',
        controllerAs: 'ctrl',
        focusOnOpen: false,
        targetEvent: event,
        templateUrl: 'templates/add-item-dialog.html',
      }).then($scope.getDesserts);
    };

    $scope.delete = function (event) {
      $mdDialog.show({
        clickOutsideToClose: true,
        controller: 'deleteController',
        controllerAs: 'ctrl',
        focusOnOpen: false,
        targetEvent: event,
        locals: { desserts: $scope.selected },
        templateUrl: 'templates/delete-dialog.html',
      }).then($scope.getDesserts);
    };

    function success(desserts) {
      $scope.desserts = desserts;
    }

    $scope.getDesserts = function () {
      $scope.promise = $nutrition.desserts.get($scope.query, success).$promise;
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

      $scope.getDesserts();
    });

  }]);

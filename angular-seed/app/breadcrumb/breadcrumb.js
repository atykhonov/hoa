'use strict';

var mod = angular.module('myApp.breadcrumb', ['ngRoute'])

mod.controller(
  'BreadcrumbCtrl',
  ['$scope',
    function ($scope) {
      $scope.$on('breadcrumb:updated', function (event, data) {
        $scope.items = data;
      });
    }]);

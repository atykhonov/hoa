'use strict';

var mod = angular.module('myApp.user', ['ngRoute'])

mod.config(['$routeProvider', function ($routeProvider) {
  $routeProvider.when('/login', {
    templateUrl: 'user/login.html',
    controller: 'UserCtrl'
  });
}]);

mod.controller(
  'UserCtrl',
  ['$scope', 'user', 'auth', '$rootScope', '$window', '$location',
    function ($scope, user, auth, $rootScope, $window, $location) {

      var self = this;

      $scope.email = '';

      $scope.password = '';

      $scope.user = {};

      if (auth.isAuthed()) {
        var userInfo = auth.getUserInfo();
        $scope.user = {
          'email': userInfo['email']
        }
      }

      function handleRequest(res) {
        var token = res.data ? res.data.token : null;
        auth.saveToken(token);

        var userInfo = undefined;
        user.getInfo().then(function (response) {
          auth.saveUserInfo(response.data);
          $location.path('/');
        });
      }

      self.parseJwt = function (token) {
        var base64Url = token.split('.')[1];
        var base64 = base64Url.replace('-', '+').replace('_', '/');
        return JSON.parse($window.atob(base64));
      }

      $scope.login = function () {
        user.login($scope.user.email, $scope.user.password)
          .then(function (response) {
            handleRequest(response);
          }, handleRequest)
      }

      $scope.logout = function () {
        auth.logout && auth.logout();
      }

      $scope.refreshToken = function () {
        user.refreshToken().then(function (response) {
          auth.refreshToken(response.data);
        });
      }

      $scope.isAuthed = function () {
        return auth.isAuthed();
      }

    }]);

mod.controller(
  'UserDialogCtrl',
  ['associations', '$mdDialog', '$resources', '$scope',
    function (associations, $mdDialog, $resources, $scope) {

      self = this;

      this.add = true;

      this.cancel = $mdDialog.cancel;

      this.associations = [];

      angular.forEach(associations.data, function (item) {
        self.associations.push({ id: item.id, name: item.name });
      });

      this.saveUser = function () {
        $scope.promise = $resources.users.create(
          $scope.user,
          function (user) {
            $mdDialog.hide(user);
          }
        ).$promise;
      }
    }]);

mod.controller(
  'UserConfirmDialogCtrl',
  ['users', '$mdDialog', '$resources', '$scope', '$q',
    function (users, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(users.forEach(deleteUser)).then(onComplete);
      }

      function deleteUser(user, index) {
        var deferred = $resources.users.delete({ id: user.id });
        deferred.$promise.then(function () {
          users.splice(index, 1);
        });
        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }
    }]);

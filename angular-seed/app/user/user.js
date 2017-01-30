'use strict';

angular.module('myApp.user', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/login', {
      templateUrl: 'user/login.html',
      controller: 'UserCtrl'
    });
  }])

  .controller(
  'UserCtrl',
  ['$scope', 'user', 'auth', '$rootScope', '$window',
    function ($scope, user, auth, $rootScope, $window) {

      var self = this;

      $scope.email = 'manager@osbb.org';

      $scope.password = 'tBZZdar4';

      function handleRequest(res) {
        var token = res.data ? res.data.token : null;
        // if (token) { console.log('JWT:', token); }
        // console.log('Response: ');
        // console.log(res);
        self.message = res.data.message;
        auth.saveToken(token);

        var userInfo = undefined;
        user.getInfo().then(function (response) {
          auth.saveUserInfo(response.data);
        });
      }

      self.parseJwt = function (token) {
        var base64Url = token.split('.')[1];
        var base64 = base64Url.replace('-', '+').replace('_', '/');
        return JSON.parse($window.atob(base64));
      }

      $scope.login = function () {
        user.login($scope.email, $scope.password)
          .then(handleRequest, handleRequest)
      }
      self.register = function () {
        user.register(self.username, self.password)
          .then(handleRequest, handleRequest)
      }
      $scope.getQuote = function () {
        user.getQuote()
          .then(handleRequest, handleRequest)
      }
      $scope.logout = function () {
        auth.logout && auth.logout()
      }
      $scope.isAuthed = function () {
        return auth.isAuthed ? auth.isAuthed() : false
      }
    }]);

'use strict';

angular.module('myApp.user', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/user', {
      templateUrl: 'user/login.html',
      controller: 'UserCtrl'
    });
  }])

  .controller('UserCtrl', ['$scope', 'user', 'auth', function ($scope, user, auth) {

    var self = this;

    function handleRequest(res) {
      var token = res.data ? res.data.token : null;
      if (token) { console.log('JWT:', token); }
      self.message = res.data.message;
      auth.saveToken(token);
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

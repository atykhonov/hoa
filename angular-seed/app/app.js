'use strict';

function authInterceptor(API, auth) {
  return {
    // automatically attach Authorization header
    request: function (config) {
      var token = auth.getToken();
      if (config.url.indexOf(API) === 0 && token) {
        config.headers.Authorization = 'JWT ' + token;
      }
      return config;
    },

    // If a token was sent back, save it
    response: function (res) {
      if (res.config.url.indexOf(API) === 0 && res.data.token) {
        auth.saveToken(res.data.token);
      }
      return res;
    },
  }
}

function authService($window) {

  var self = this;

  self.parseJwt = function (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse($window.atob(base64));
  }

  self.saveToken = function (token) {
    $window.localStorage['jwtToken'] = token;
  }

  self.getToken = function () {
    return $window.localStorage['jwtToken'];
  }

  self.isAuthed = function () {
    var token = self.getToken();
    if (token) {
      var params = self.parseJwt(token);
      return Math.round(new Date().getTime() / 1000) <= params.exp;
    } else {
      return false;
    }
  }

  self.logout = function () {
    $window.localStorage.removeItem('jwtToken');
  }
}

function userService($http, API, auth) {
  var self = this;
  self.getQuote = function () {
    return $http.get(API + 'api-token-auth/quote')
  }

  self.login = function (email, password) {
    return $http.post(API + 'api-token-auth/', {
      email: email,
      password: password
    })
  };
}

// Declare app level module which depends on views, and components
angular.module('myApp', [
  'ngResource',
  'ngMaterial',
  'md.data.table',
  'ngRoute',
  'myApp.view1',
  'myApp.view2',
  'myApp.version',
  'myApp.mdtable',
  'myApp.user',
  'myApp.association',
  'myApp.house',
  'myApp.apartment',
  'myApp.account',
  'myApp.service',
  'myApp.navbar'
])
  .factory('authInterceptor', authInterceptor)
  .factory('$resources', ['$resource', function ($resource) {
    return {
      cooperatives: $resource('http://localhost:8080/api/v1/cooperatives/:id/'),
      assoc_houses: $resource(
        'http://localhost:8080/api/v1/cooperatives/:cooperative_id/houses/',
        // TODO: user just a simple id instead of cooperative_id or house_id.
        { cooperative_id: '@cooperative_id' }),
      houses: $resource('http://localhost:8080/api/v1/houses/:id/'),
      house_apartments: $resource(
        'http://localhost:8080/api/v1/houses/:house_id/apartments/',
        { house_id: '@house_id' }),
      apartments: $resource('http://localhost:8080/api/v1/apartments/:id/'),
      apartment_account: $resource('http://localhost:8080/api/v1/apartments/:id/account/'),
      accounts: $resource('http://localhost:8080/api/v1/accounts/:id/'),
      services: $resource('http://localhost:8080/api/v1/services/:id/'),
      cooperative_services: $resource(
        'http://localhost:8080/api/v1/cooperatives/:cooperative_id/services/',
        { cooperative_id: '@cooperative_id' }),
      units: $resource('http://localhost:8080/api/v1/units/'),
    };
  }])
  .service('user', userService)
  .service('auth', authService)
  .constant('API', 'http://localhost:8080/')
  .config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
    $locationProvider.hashPrefix('!');
    $routeProvider.otherwise({ redirectTo: '/' });
  }])
  .config(['$httpProvider', '$mdThemingProvider', function ($httpProvider, $mdThemingProvider) {
    $httpProvider.interceptors.push('authInterceptor');
    $mdThemingProvider.theme('default')
      .primaryPalette('blue')
      .accentPalette('deep-orange');
  }])
  .config(['$resourceProvider', function ($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $resourceProvider.defaults.actions = {
      create: { method: 'POST' },
      get: { method: 'GET' },
      getAll: { method: 'GET', isArray: true },
      update: { method: 'PUT' },
      delete: { method: 'DELETE' }
    };
  }])
  .run(['$rootScope', '$location', '$routeParams', '$window', '$http', function ($rootScope, $location, $routeParams, $window, $http) {
    $rootScope.$on('$routeChangeSuccess', function (e, current, pre) {
      if (current.$$route !== undefined) {
        $rootScope.currentNavItem = 'associations';
        if (current.$$route.originalPath == '/associations/:id/houses') {
          $rootScope.currentNavItem = 'houses';
        }
      }
    });

    // keep user logged in after page refresh
    if ($window.localStorage['jwtToken']) {
      $http.defaults.headers.common.Authorization = 'JWT ' + $window.localStorage['jwtToken'];
    }

    // redirect to login page if not logged in and trying to access a restricted page
    $rootScope.$on('$locationChangeStart', function (event, next, current) {
      var publicPages = ['/user'];
      var restrictedPage = publicPages.indexOf($location.path()) === -1;
      if (restrictedPage && !$window.localStorage['jwtToken']) {
        $location.path('/user');
      }
    });
  }])
  .controller('RootController', ['$scope', function ($scope, $state) {
    $scope.currentNavItem = 'associations';
  }])

  .filter("trust", ['$sce', function ($sce) {
    return function (htmlCode) {
      return $sce.trustAsHtml(htmlCode);
    }
  }]);


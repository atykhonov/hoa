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

function authService($window, store) {

  var self = this;

  self.parseJwt = function (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse($window.atob(base64));
  }

  self.saveToken = function (token) {
    // $window.localStorage['jwtToken'] = token;
    store.set('jwt', token);
  }

  self.getToken = function () {
    return store.get('jwt');
    // return $window.localStorage['jwtToken'];
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
var app = angular.module('myApp', [
  'ngResource',
  'ngMaterial',
  'md.data.table',
  'angular-storage',
  'ngRoute',
  'angular-jwt',
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
]);

// .factory('authInterceptor', authInterceptor)

app.factory('$resources', ['$resource', function ($resource) {
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
}]);

app.service('user', userService);
app.service('auth', authService);
app.constant('API', 'http://localhost:8080/');
app.config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');
  $routeProvider.otherwise({ redirectTo: '/' });
}]);

app.config(
  ['$httpProvider', '$mdThemingProvider', 'jwtOptionsProvider', 'jwtInterceptorProvider',
    function ($httpProvider, $mdThemingProvider, jwtOptionsProvider, jwtInterceptorProvider) {

      // $httpProvider.interceptors.push('authInterceptor');

      jwtOptionsProvider.config({
        authPrefix: 'JWT ',
        whiteListedDomains: ['127.0.0.1', 'localhost']
      });

      jwtInterceptorProvider.tokenGetter = function (store) {
        return store.get('jwt');
      };

      // jwtInterceptorProvider.tokenGetter = function (store) {
      //   return $window.localStorage.get('id_token');
      // }

      // jwtOptionsProvider.config({
      //   tokenGetter: ['myService', function (myService) {
      //     myService.doSomething();
      //     return localStorage.getItem('id_token');
      //   }]
      // });

      $httpProvider.interceptors.push('jwtInterceptor');

      $mdThemingProvider.theme('default')
        .primaryPalette('blue')
        .accentPalette('deep-orange');
    }
  ]
);

app.config(['$resourceProvider', function ($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
  $resourceProvider.defaults.actions = {
    create: { method: 'POST' },
    get: { method: 'GET' },
    getAll: { method: 'GET', isArray: true },
    update: { method: 'PUT' },
    delete: { method: 'DELETE' }
  };
}]);

app.run(
  ['$rootScope', '$location', '$routeParams', '$window', '$http', 'authManager', 'store', 'jwtHelper',
    function ($rootScope, $location, $routeParams, $window, $http, authManager, store, jwtHelper) {

      authManager.checkAuthOnRefresh();

      $rootScope.$on('$routeChangeSuccess', function (e, current, pre) {
        if (current.$$route !== undefined) {
          $rootScope.currentNavItem = 'associations';
          if (current.$$route.originalPath == '/associations/:id/houses') {
            $rootScope.currentNavItem = 'houses';
          }
        }
      });

      // keep user logged in after page refresh
      // if ($window.localStorage['jwtToken']) {
      //   $http.defaults.headers.common.Authorization = 'JWT ' + $window.localStorage['jwtToken'];
      // }

      // redirect to login page if not logged in and trying to access a restricted page
      // $rootScope.$on('$locationChangeStart', function (event, next, current) {
      //   var publicPages = ['/user'];
      //   var restrictedPage = publicPages.indexOf($location.path()) === -1;
      //   if (restrictedPage && !$window.localStorage['jwtToken']) {
      //     $location.path('/user');
      //   }
      // });

      $rootScope.$on('$stateChangeStart', function (e, to) {
        if (to.data && to.data.requiresLogin) {
          if (!store.get('jwt') || jwtHelper.isTokenExpired(store.get('jwt'))) {
            e.preventDefault();
            // $state.go('login');
            $location.path('/login');
            console.log('Go to login!!!');
          }
        }
      });
    }
  ]
);

app.controller('RootController', ['$scope', function ($scope, $state) {
  $scope.currentNavItem = 'associations';
}])

app.filter("trust", ['$sce', function ($sce) {
  return function (htmlCode) {
    return $sce.trustAsHtml(htmlCode);
  }
}]);


'use strict';

function authService($window, store) {

  var self = this;

  self.parseJwt = function (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse($window.atob(base64));
  }

  self.saveToken = function (token) {
    store.set('jwt', token);
  }

  self.saveUserInfo = function (info) {
    store.set('info', info);
  }

  self.getUserInfo = function () {
    return store.get('info');
  }

  self.getToken = function () {
    return store.get('jwt');
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

  self.needsFreshToken = function () {
    var token = self.getToken();
    if (token) {
      var now = Math.round(new Date().getTime() / 1000);
      var params = self.parseJwt(token);
      if (params.exp - now < 5 * 60) {
        return true;
      }
    } else {
      return false;
    }
  }

  self.logout = function () {
    store.set('jwt', null);
    store.set('info', null);
  }
}

function userService($http, API, auth) {

  var self = this;

  self.login = function (email, password) {
    return $http.post(API + 'api-token-auth/', {
      email: email,
      password: password
    })
  };

  self.getInfo = function () {
    return $http.get(API + 'api/v1/user-info/');
  };

  self.refreshToken = function () {
    var token = auth.getToken();
    return $http.post(API + 'api-token-refresh/', { token: token });
  }
}

function BreadcrumbService($rootScope, $http, API) {

  var self = this;

  self.items = [];

  this.addItem = function (item) {
    self.items.push(item);
  }

  this.setItems = function (items) {
    self.items = items;
  }

  this.getItems = function () {
    return self.items;
  }

  this.init = function (params) {
    $http.get(API + 'api/v1/breadcrumb/', { params: params }).then(function (response) {
      self.setItems(response);
      $rootScope.$broadcast('breadcrumb:updated', response.data);
    });
  }
}

// Declare app level module which depends on views, and components
var app = angular.module('myApp', [
  'ngResource',
  'ngMaterial',
  'md.data.table',
  'angular-storage',
  'angularMoment',
  'ngRoute',
  'angular-jwt',
  'myApp.root',
  'myApp.view1',
  'myApp.view2',
  'myApp.version',
  'myApp.mdtable',
  'myApp.admin',
  'myApp.user',
  'myApp.association',
  'myApp.house',
  'myApp.apartment',
  'myApp.account',
  'myApp.service',
  'myApp.charge',
  'myApp.meter',
  'myApp.indicator',
  'myApp.navbar',
  'myApp.breadcrumb'
]);

app.factory('$resources', ['$resource', 'APIV1', function ($resource, APIV1) {
  return {
    cooperatives: $resource(APIV1 + 'cooperatives/:id/'),
    associations: $resource(APIV1 + 'cooperatives/:id/'),
    assoc_houses: $resource(APIV1 + 'cooperatives/:cooperative_id/houses/',
      // TODO: user just a simple id instead of cooperative_id or house_id.
      { cooperative_id: '@cooperative_id' }),
    houses: $resource(APIV1 + 'houses/:id/'),
    house_apartments: $resource(
      APIV1 + 'houses/:house_id/apartments/',
      { house_id: '@house_id' }),
    house_accounts: $resource(
      APIV1 + 'houses/:house_id/accounts/',
      { house_id: '@house_id' }),
    apartments: $resource(APIV1 + 'apartments/:id/'),
    apartment_account: $resource(APIV1 + 'apartments/:id/account/'),
    accounts: $resource(APIV1 + 'accounts/:id/'),
    services: $resource(APIV1 + 'services/:id/'),
    users: $resource(APIV1 + 'users/:id/'),
    cooperative_services: $resource(
      APIV1 + 'cooperatives/:cooperative_id/services/',
      { cooperative_id: '@cooperative_id' }),
    house_services: $resource(
      APIV1 + 'houses/:house_id/services/',
      { house_id: '@house_id' }),
    house_charges: $resource(
      APIV1 + 'houses/:house_id/charges/',
      { house_id: '@house_id' }),
    apartment_services: $resource(
      APIV1 + 'apartments/:apartment_id/services/',
      { apartment_id: '@apartment_id' }),
    apartment_charges: $resource(
      APIV1 + 'apartments/:apartment_id/charges/',
      { apartment_id: '@apartment_id' }),
    assoc_services: $resource(
      APIV1 + 'cooperatives/:cooperative_id/services/',
      { cooperative_id: '@cooperative_id' }),
    units: $resource(APIV1 + 'units/'),
    cooperative_indicators: $resource(
      APIV1 + 'cooperatives/:cooperative_id/indicators/'),
    house_indicators: $resource(
      APIV1 + 'houses/:house_id/indicators/',
      { house_id: '@house_id' }),
    apartment_indicators: $resource(
      APIV1 + 'apartments/:apartment_id/indicators/',
      { apartment_id: '@apartment_id' }),
    cooperative_recalccharges: $resource(
      APIV1 + 'cooperatives/:cooperative_id/recalccharges/',
      { cooperative_id: '@cooperative_id' }),
    house_recalccharges: $resource(
      APIV1 + 'houses/:house_id/recalccharges/',
      { house_id: '@house_id' }, { query: { method: 'POST', isArray: true } }),
    indicators: $resource(
      APIV1 + 'indicators/:indicator_id/', { indicator_id: '@indicator_id' }),
    charges: $resource(APIV1 + 'charges/')
  };
}]);

var API_URL = 'http://192.168.0.3:8080/';

app.service('user', userService);
app.service('auth', authService);
app.service('breadcrumb', BreadcrumbService);

app.constant('API', API_URL);
app.constant('APIV1', API_URL + 'api/v1/');

app.config(function ($compileProvider) {
  $compileProvider.preAssignBindingsEnabled(true);
});

app.config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');
  $routeProvider.otherwise({ redirectTo: '/' });
}]);

app.config(
  ['$httpProvider', '$mdThemingProvider',
    function ($httpProvider, $mdThemingProvider) {

      $httpProvider.interceptors.push('authInterceptor');

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
    update: { method: 'PATCH' },
    delete: { method: 'DELETE' },
    recalc: { method: 'POST', isArray: true },
  };
}]);

app.run(
  ['$rootScope', 'auth', '$location',
    function ($rootScope, auth, $location) {
      $rootScope.$on('$routeChangeSuccess', function (e, current, pre) {
        var route = current.$$route;
        if (route !== undefined && route.originalPath == '/login') {
          return;
        }
        if (!auth.isAuthed()) {
          e.preventDefault();
          return $location.path("/login");
        }
      });
    }
  ]
);

app.filter('trust', ['$sce', function ($sce) {
  return function (htmlCode) {
    return $sce.trustAsHtml(htmlCode);
  }
}]);

app.filter('replace_space', [function () {

  return function (value, num) {

    var result = '';
    var results = value.split(' ');
    for (var i = 0; i < results.length; i++) {
      var sep = ' ';
      if (i == 0) {
        sep = '';
      }
      if (i == num) {
        sep = '<br />';
      }
      result += sep + results[i];
    }
    return result;
  }
}]);

app.factory(
  'authInterceptor',
  ['auth', '$rootScope', '$injector', 'API',
    function (auth, $rootScope, $injector, API) {

      var authInterceptor = {

        request: function (config) {
          var token = auth.getToken();
          if (config.url.indexOf(API) === 0 && token) {
            config.headers.Authorization = 'JWT ' + token;
          }
          return config;
        },

        response: function (response) {
          if (auth.isAuthed() && auth.needsFreshToken()) {
            var user = $injector.get('user');
            user.refreshToken().then(function (response) {
              var token = response.data ? response.data.token : null;
              auth.saveToken(token);
            });
          }
          if (response.config.url.indexOf(API) === 0 && response.data.token) {
            auth.saveToken(response.data.token);
          }
          return response;
        },

        responseError: function (response) {
          if (response.status === 401) {
            $rootScope.$broadcast('unauthorized');
          }
          return response;
        }
      };

      return authInterceptor;

    }]);

angular.module("myApp.root", [], function ($routeProvider) {
  $routeProvider.when('/', {
    resolve: {
      controller: 'RootCtrl'
    }
  });
});

app.factory('RootCtrl', ['$location', 'auth', function ($location, auth) {

  var userInfo = auth.getUserInfo();

  if (userInfo === undefined) {
    $location.path('/login');
  }

  if (userInfo['is_superuser']) {
    $location.path('/admin');
  } else {
    $location.path('/associations/' + userInfo['cooperative_id'] + '/');
  }

}]);

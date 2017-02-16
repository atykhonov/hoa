'use strict';

angular.module('myApp.apartment', ['ngRoute'])

  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/houses/:id/apartments', {
      templateUrl: 'apartment/apartment.html',
      controller: 'ApartmentCtrl'
    });
    $routeProvider.when('/apartments', {
      templateUrl: 'apartment/apartment.html',
      controller: 'ApartmentCtrl'
    });
    $routeProvider.when('/apartments/:apartmentId/', {
      templateUrl: 'apartment/apartment-details.html',
      controller: 'ApartmentDetailsCtrl'
    });
  }])

  .controller(
  'ApartmentCtrl',
  ['$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

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

      $scope.addApartment = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'AddApartmentController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          templateUrl: 'apartment/add-apartment-dialog.html',
        }).then($scope.getApartments);
      };

      $scope.deleteApartment = function (event) {
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'DeleteApartmentController',
          controllerAs: 'ctrl',
          focusOnOpen: false,
          targetEvent: event,
          locals: { apartments: $scope.selected },
          templateUrl: 'apartment/delete-dialog.html',
        }).then($scope.getApartments);
      };

      $scope.editApartment = function (event) {
        if ($scope.selected.length > 1) {
          alert('Для редагування виберіть тільки один елемент.');
        } else {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'EditApartmentController',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { apartment: $scope.selected[0] },
            templateUrl: 'apartment/add-apartment-dialog.html',
          }).then($scope.getApartments);
        }
      };

      $scope.editAccount = function (event, apartment_id) {

        event.stopPropagation();

        var apartment = undefined;
        var apartments = $scope.apartments.data;
        for (var i = 0; i < apartments.length; i++) {
          if (apartments[i].id == apartment_id) {
            apartment = apartments[i];
            break;
          }
        }
        console.log(apartment_id);
        console.log('Found apartment: ');
        console.log(apartment);
        console.log('All apartments: ');
        console.log(apartments);
        $mdDialog.show({
          clickOutsideToClose: true,
          controller: 'EditApartmentAccountController',
          controllerAs: 'ctrl',
          focusOnOpen: true,
          targetEvent: event,
          locals: { apartment: apartment },
          templateUrl: 'apartment/edit-account-dialog.html',
        }).then($scope.getApartments);
      }

      function success(apartments) {
        $scope.apartments = apartments;
      }

      $scope.getApartments = function () {
        var query = $scope.query;
        if ($routeParams.id !== undefined) {
          query['house_id'] = $routeParams.id;
          $scope.promise = $resources.house_apartments.get(
            $scope.query, success).$promise;
        } else {
          $scope.promise = $resources.apartments.get(
            $scope.query, success).$promise;
        }
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

        $scope.getApartments();
      });

    }])

  .controller('AddApartmentController',
  ['$mdDialog', '$resources', '$scope', '$routeParams',
    function ($mdDialog, $resources, $scope, $routeParams) {

      this.add = true;

      this.cancel = $mdDialog.cancel;

      function success(apartment) {
        $mdDialog.hide(apartment);
      }

      this.addApartment = function () {
        $scope.apartment['house_id'] = $routeParams.id;
        $scope.promise = $resources.house_apartments.create($scope.apartment, success).$promise;
      }
    }])

  .controller('DeleteApartmentController',
  ['apartments', '$mdDialog', '$resources', '$scope', '$q',
    function (apartments, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.deletionConfirmed = function () {
        $q.all(apartments.forEach(deleteApartment)).then(onComplete);
      }

      function deleteApartment(apartment, index) {
        var deferred = $resources.apartments.delete({ id: apartment.id });

        deferred.$promise.then(function () {
          apartments.splice(index, 1);
        });

        return deferred.$promise;
      }

      function onComplete() {
        $mdDialog.hide();
      }

    }])

  .controller('EditApartmentController',
  ['apartment', '$mdDialog', '$resources', '$scope', '$q',
    function (apartment, $mdDialog, $resources, $scope, $q) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.apartment = JSON.parse(JSON.stringify(apartment));

      this.updateApartment = function () {
        var deferred = $resources.apartments.update({ id: apartment.id }, $scope.apartment);
        deferred.$promise.then(function () {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }

    }])

  .controller(
  'EditApartmentAccountController',
  ['apartment', '$mdDialog', '$resources', '$scope', '$q',
    function (apartment, $mdDialog, $resources, $scope, $q) {

      this.cancel = $mdDialog.cancel;

      this.updateAccount = function () {
        var deferred = $resources.apartment_account.update({ id: apartment.id }, $scope.account);
        deferred.$promise.then(function () {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }

    }])

  .controller(
  'ApartmentDialogCtrl',
  ['apartment', '$scope', '$resources', '$mdDialog',
    function (apartment, $scope, $resources, $mdDialog) {

      this.edit = true;

      this.cancel = $mdDialog.cancel;

      $scope.apartment = JSON.parse(JSON.stringify(apartment));

      this.saveApartment = function () {
        var deferred = $resources.apartments.update({ id: apartment.id }, $scope.apartment);
        deferred.$promise.then(function () {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }
    }])

  .controller(
  'ApartmentDetailsCtrl',
  ['$scope', '$resources', '$routeParams', '$mdDialog', 'moment', '$mdEditDialog', 'breadcrumb',
    function ($scope, $resources, $routeParams, $mdDialog, moment, $mdEditDialog, breadcrumb) {

      breadcrumb.init($routeParams);

      var apartmentBlock = function (apartmentId) {
        $scope.apartmentPromise = $resources.apartments.get(
          { id: apartmentId },
          function (apartment) {
            $scope.apartment = apartment;
          }
        ).$promise;

        $scope.editApartment = function (event, apartment) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'ApartmentModalCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { apartment: apartment },
            templateUrl: 'apartment/apartment-dialog.html',
          }).then(function () {
            apartmentBlock(apartment.id);
          });
        };
      }

      var accountBlock = function (apartmentId) {
        $scope.editAccount = function (event, account) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'AccountDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { account: account },
            templateUrl: 'account/account-dialog.html',
          }).then(function () {
            apartmentBlock(apartmentId);
          });
        };
      }

      var indicatorsBlock = function (apartmentId) {

        $scope.selectedIndicators = [];

        $scope.filter = {
          options: {
            debounce: 500
          }
        };

        $scope.indicatorsQuery = {
          filter: '',
          limit: '5',
          order: 'id',
          page: 1,
          period: new Date(moment({ day: 1 }).format("YYYY-MM-DD")),
        };

        $scope.getIndicators = function () {
          var query = $scope.indicatorsQuery;
          query['apartment_id'] = apartmentId;
          $scope.indicatorsPromise = $resources.apartment_indicators.get(
            query,
            function (indicators) {
              $scope.indicators = indicators;
            }
          ).$promise;
        };

        $scope.$watch(
          'indicatorsQuery.period',
          function (newValue, oldValue) {
            $scope.getIndicators();
          }
        );

        $scope.editIndicator = function (event) {
          $mdDialog.show({
            clickOutsideToClose: true,
            controller: 'IndicatorDialogCtrl',
            controllerAs: 'ctrl',
            focusOnOpen: true,
            targetEvent: event,
            locals: { indicator: $scope.selectedIndicators[0] },
            templateUrl: 'indicator/indicator-dialog.html',
          }).then($scope.getIndicators);
        };

        $scope.editIndicatorInline = function (event, indicator) {

          self = this;

          event.stopPropagation();

          this.saveIndicator = function (indicator) {
            var data = {
              'value': indicator.value,
            };
            $scope.promise = $resources.indicators.update(
              { 'indicator_id': indicator.id },
              data,
              function (indicator) {
                $mdDialog.hide(indicator);
              }).$promise;
          }

          var promise = $mdEditDialog.large({
            'title': 'Показник',
            'cancel': 'Відмінити',
            'ok': 'Зберегти',
            messages: {
              test: ' '
            },
            'type': 'number',
            modelValue: indicator.value,
            placeholder: 'Введіть показник',
            save: function (input) {
              indicator.value = input.$modelValue;
              self.saveIndicator(indicator);
            },
            targetEvent: event
          });

          promise.then(function (ctrl) {
            var input = ctrl.getInput();

            input.$viewChangeListeners.push(function () {
              input.$setValidity('test', input.$modelValue !== 'test');
            });
          });
        }
      }

      var chargesBlock = function (apartmentId) {

        $scope.filter = {
          options: {
            debounce: 500
          }
        };

        $scope.chargesQuery = {
          filter: '',
          limit: '5',
          order: 'id',
          page: 1
        };

        function success(response) {
          var charges = [];
          angular.forEach(response.data, function (charge, id) {
            var item = {
              'id': charge.id,
              'pid': charge.pid,
              'address': charge.address,
              'service_charges': [],
              'total': charge.total
            };
            angular.forEach($scope.services, function (service) {
              var service_charge_value = 0;
              angular.forEach(charge.services, function (service_charge, id) {
                if (service_charge.service.id == service.id) {
                  service_charge_value = service_charge.value;
                }
              });
              item['service_charges'].push({
                'value': service_charge_value
              });
            });
            charges.push(item);
          });
          charges.count = response.count;
          $scope.charges = charges;
        }

        function success_services(response) {
          var services = [];
          angular.forEach(response.data, function (assoc_service, id) {
            services.push({
              'id': assoc_service.service.id,
              'name': assoc_service.service.name
            });
          });
          $scope.services = services;
          $scope.getCharges();
        }

        $scope.getCharges = function () {
          var query = $scope.query;
          $scope.chargesPromise = $resources.charges.get($scope.query, success).$promise;
        };

        $scope.getServices = function () {
          $scope.services_promise = $resources.cooperative_services.get(
            { cooperative_id: associationId }, success_services).$promise;
        }
      }

      var apartmentId = $routeParams.apartmentId;
      apartmentBlock(apartmentId);
      accountBlock(apartmentId);
      indicatorsBlock(apartmentId);
      chargesBlock(apartmentId);

    }])

  .controller(
  'ApartmentModalCtrl', [
    'apartment', '$mdDialog', '$resources', '$scope', 'auth',
    function (apartment, $mdDialog, $resources, $scope, auth) {

      this.cancel = $mdDialog.cancel;

      if ('id' in apartment) {
        $scope.apartment = JSON.parse(JSON.stringify(apartment));
      } else {
        $scope.apartment = {};
      }

      this.addApartment = function () {
        $scope.apartment['house_id'] = apartment['houseId'];
        $scope.promise = $resources.assoc_houses.create(
          $scope.apartment,
          function (apartment) {
            $mdDialog.hide(apartment);
          }
        ).$promise;
      }

      this.saveApartment = function () {
        var deferred = $resources.apartments.update({ id: apartment.id }, $scope.apartment);
        deferred.$promise.then(function (apartment) {
          $mdDialog.hide(apartment);
        });
        return deferred.$promise;
      }
    }])

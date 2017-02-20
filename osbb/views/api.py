# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from osbb.models import (
    Account,
    Apartment,
    BankAccount,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService as HCService,
    Meter,
    MeterIndicator,
    Service,
    UNITS,
    User,
)
from osbb.permissions import (
    IsInhabitant,
    IsManager,
    NoPermissions,
)
from osbb.serializers import (
    AccountSerializer,
    ApartmentSerializer,
    BankAccountSerializer,
    ChargeSerializer,
    HouseSerializer,
    HousingCooperativeSerializer as HCSerializer,
    HousingCooperativeServiceSerializer as HCServiceSerializer,
    MeterSerializer,
    MeterIndicatorSerializer,
    ServiceSerializer,
    UserSerializer,
)
from osbb.utils import calccharges


class BaseModelViewSet(viewsets.ModelViewSet):

    authentication_classes = (JSONWebTokenAuthentication, )

    def _get_permission_denied_response(self):
        """
        Return permission denied response.
        """
        return Response({
            'details': 'You do not have permission to perform this action.',
            }, status=status.HTTP_403_FORBIDDEN)

    def get_page(self, request):
        """
        Retrieve from the `request` and return `page` parameter.
        """
        try:
            page = int(request.query_params.get('page'))
        except (ValueError, TypeError):
            page = 1
        page -= 1
        return page

    def get_limit(self, request):
        """
        Retrieve from the `request` and return `limit` parameter.
        """
        try:
            limit = int(request.query_params.get('limit'))
        except (ValueError, TypeError):
            limit = 5
        return limit

    def list_paginated(
            self, request, queryset, serializer_class, order_by=None):
        if order_by is None:
            order_by = request.query_params.get('order', '')
        limit = self.get_limit(request)
        offset = self.get_page(request) * limit
        limit = offset + limit
        qset = queryset.all()
        if order_by:
            qset = qset.order_by(order_by)
        qset = qset[offset:limit]
        serializer = serializer_class(qset, many=True)
        data = {
            'data': serializer.data,
            'count': queryset.count(),
        }
        return Response(data)


class CooperativeServicesMixin():

    def process_services_get_request(self, request, cooperative):
        hc_services = HCService.objects.filter(cooperative=cooperative)
        return self.list_paginated(
            request, hc_services, HCServiceSerializer)

    def process_charges_get_request(self, request, queryset):
        return self.list_paginated(request, queryset, ChargeSerializer)

    def process_recalc_charges(self, request, house=None, apartment=None):
        charges = calccharges(house=house, apartment=apartment)
        context = {
            'request': request,
        }
        serializer = ChargeSerializer(charges, many=True, context=context)
        return Response(serializer.data)


class HousingCooperativeViewSet(BaseModelViewSet, CooperativeServicesMixin):
    """
    API endpoint that allows cooperatives to be viewed or edited.
    """
    queryset = HousingCooperative.objects.all()
    serializer_class = HCSerializer

    def get_permissions(self):
        """
        Admin user is granted to add/change/delete a cooperative, but a
        manager is granted only to change it.
        """
        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )

    def create(self, request):
        if request.user.is_staff and not request.user.is_superuser:
            return self._get_permission_denied_response()
        return super(HousingCooperativeViewSet, self).create(request)

    def list(self, request):
        if request.user.is_staff and not request.user.is_superuser:
            return self._get_permission_denied_response()
        return self.list_paginated(
            request, HousingCooperative.objects, HCSerializer)

    @detail_route(methods=['get', 'post'])
    def houses(self, request, pk):
        """
        Return the houses of the cooperative or create a new house.
        """
        cooperative = HousingCooperative.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            houses = House.objects.filter(cooperative=pk)
            return self.list_paginated(request, houses, HouseSerializer)
        elif request.method == 'POST':
            request.data['cooperative'] = cooperative.id
            serializer = HouseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)

            return Response({
                'status': 'Bad Request',
                'message': 'House could not be created with received data'
            }, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get', 'post', 'delete', 'patch', ])
    def services(self, request, pk):
        """
        Return the services of the cooperative.
        """
        cooperative = HousingCooperative.objects.get(pk=pk)
        user = request.user
        # if not user.is_superuser:
        #     return self._get_permission_denied_response()
        if request.method == 'GET':
            return self.process_services_get_request(request, cooperative)
        elif request.method == 'PATCH':
            saved_service_ids = []
            assoc_service_ids = []
            service_ids = request.data
            for service_id in service_ids:
                service = Service.objects.get(pk=service_id)
                data = {
                    'cooperative': cooperative.id,
                    'service': service.id,
                }
                serializer = HCServiceSerializer(data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                validated_data = serializer.validated_data
                hc_service = HCService(
                    cooperative=cooperative,
                    service=service,
                    **validated_data
                    )
                try:
                    hc_service.save()
                    saved_service_ids.append(service.id)
                    assoc_service_ids.append(hc_service.id)
                except IntegrityError:
                    pass
                    # message = _(
                    #     'For the given condominium service already exists')
                    # return Response(
                    #     message, status=status.HTTP_400_BAD_REQUEST)
            for coop_service in cooperative.services.all():
                if coop_service.service.id not in service_ids:
                    coop_service.delete()
                    # The cooperative service is deleted. This is
                    # ok. But probably we should also delete all
                    # related meters and meter indicators!
            response_data = {
                'cooperative': cooperative.id,
                'services': saved_service_ids,
                'cooperative_services': assoc_service_ids,
                'notes': validated_data.get('notes'),
            }
            return Response(
                response_data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                hc_service_id = int(request.query_params.get('service_id'))
            except ValueError:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            hc_service = HCService.objects.get(pk=hc_service_id)
            hc_service.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'])
    def indicators(self, request, pk):
        """
        Return the indicators of the meters.
        """
        cooperative = HousingCooperative.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            period = parse(request.query_params.get('period'))
            indicators = MeterIndicator.objects.filter(
                meter__apartment__house__cooperative=cooperative,
                period=period
                )
            return self.list_paginated(
                request, indicators, MeterIndicatorSerializer)

    @detail_route(methods=['get', 'post'])
    def bank_accounts(self, request, pk):
        """
        Return bank accounts of the cooperative.
        """
        cooperative = HousingCooperative.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            bank_accounts = BankAccount.objects.filter(cooperative=cooperative)
            return self.list_paginated(
                request, bank_accounts, BankAccountSerializer)
        elif request.method == 'POST':
            request.data['cooperative'] = cooperative.id
            serializer = BankAccountSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)


class HouseViewSet(BaseModelViewSet, CooperativeServicesMixin):
    """
    API endpoint that allows houses to be viewed or edited.
    """
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    def get_permissions(self):
        """
        Admin user is granted to add/change/delete a cooperative, but a
        manager is granted only to change it.
        """
        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )

    def list(self, request):
        if request.user.is_superuser:
            houses = House.objects.all()
        else:
            houses = House.objects.filter(
                cooperative=request.user.cooperative)

        return self.list_paginated(request, houses, HouseSerializer)

    def update(self, request, *args, **kwargs):
        house = get_object_or_404(House, pk=kwargs.get('pk'))
        address = house.address
        street_name = request.data.get('street', address.street.name)
        house_number = request.data.get('number', address.house.number)
        address.street.name = street_name
        address.street.type = address.street.get_default_type()
        address.street.save()
        address.house.number = house_number
        address.house.save()
        serializer = HouseSerializer(house, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get', 'post'])
    def apartments(self, request, pk):
        """
        Return the apartments of the house or create a new apartment.
        """
        house = House.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(house.cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            apartments = Apartment.objects.filter(house=pk)
            return self.list_paginated(
                request, apartments, ApartmentSerializer)
        elif request.method == 'POST':
            serializer = ApartmentSerializer(data=request.data)
            if serializer.is_valid():
                apartment = Apartment.objects.create(
                    house=house, **serializer.validated_data)
                for service in Service.objects.filter(requires_meter=True):
                    meter = Meter.objects.create(
                        apartment=apartment, service=service)
                    meter.create_indicators()
                account = Account.objects.create(apartment=apartment)
                account.create_balance()
                response_data = serializer.validated_data
                response_data['id'] = apartment.id
                return Response(
                    response_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def indicators(self, request, pk):
        """
        Return all indicators which belongs to the house.
        """
        house = House.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(house.cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            period = parse(request.query_params.get('period'))
            indicators = MeterIndicator.objects.filter(
                meter__apartment__house=house,
                period=period
                )
            return self.list_paginated(
                request, indicators, MeterIndicatorSerializer)

    @detail_route(methods=['get'])
    def accounts(self, request, pk):
        """
        Return all accounts which belongs to the house.
        """
        house = House.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(house.cooperative):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            accounts = Account.objects.filter(apartment__house=house)
            return self.list_paginated(request, accounts, AccountSerializer)

    @detail_route(methods=['get'])
    def services(self, request, pk):
        house = House.objects.get(pk=pk)
        return self.process_services_get_request(request, house.cooperative)

    @detail_route(methods=['get'])
    def charges(self, request, pk):
        """
        Return the charges of the house.
        """
        house = House.objects.get(pk=pk)
        queryset = Charge.objects.filter(account__apartment__house=house)
        return self.process_charges_get_request(request, queryset)

    @detail_route(methods=['post'])
    def recalccharges(self, request, pk=None):
        house = House.objects.get(pk=pk)
        return self.process_recalc_charges(request, house=house)


class ApartmentViewSet(BaseModelViewSet, CooperativeServicesMixin):
    """
    API endpoint that allows apartments to be viewed or edited.
    """
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        if user.account:
            return (IsInhabitant(), )

        return (NoPermissions(), )

    def list(self, request):
        if request.user.is_superuser:
            apartments = Apartment.objects.all()
        else:
            apartments = Apartment.objects.filter(
                house__cooperative=request.user.cooperative)

        return self.list_paginated(request, apartments, ApartmentSerializer)

    @detail_route(methods=['get', 'post'])
    def meters(self, request, pk):
        """
        Return the meters of the house or create a new meter.
        """
        apartment = Apartment.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(apartment):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            apartment_meters = ApartmentMeter.objects.filter(apartment=pk)
            context = {
                'request': request,
            }
            meters = [m.meter for m in apartment_meters]
            serializer = MeterSerializer(meters, many=True, context=context)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = MeterSerializer(data=request.data)
            if serializer.is_valid():
                meter = Meter(**serializer.validated_data)
                meter.save()
                meter = ApartmentMeter(apartment=apartment, meter=meter)
                meter.save()
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get', 'put'])
    def account(self, request, pk):
        """
        Return the account of the apartment or update the account.
        """
        apartment = Apartment.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(apartment):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            account = Account.objects.filter(apartment=pk)
            context = {
                'request': request,
            }
            serializer = AccountSerializer(account, context=context)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            account = apartment.account
            serializer = AccountSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                account.first_name = validated_data.get('first_name')
                account.last_name = validated_data.get('last_name')
                account.save()
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def indicators(self, request, pk):
        """
        Return all indicators which belongs to the apartment.
        """
        apartment = Apartment.objects.get(pk=pk)
        user = request.user
        if (not user.can_manage(apartment.house.cooperative)
             and not user.is_owner(apartment)):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            period = parse(request.query_params.get('period'))
            indicators = MeterIndicator.objects.filter(
                meter__apartment=apartment,
                period=period
                )
            return self.list_paginated(
                request, indicators, MeterIndicatorSerializer)

    @detail_route(methods=['get'])
    def services(self, request, pk):
        apartment = Apartment.objects.get(pk=pk)
        return self.process_services_get_request(
            request, apartment.house.cooperative)

    @detail_route(methods=['get'])
    def charges(self, request, pk):
        """
        Return the charges of the house.
        """
        apartment = Apartment.objects.get(pk=pk)
        queryset = Charge.objects.filter(account__apartment=apartment)
        return self.process_charges_get_request(request, queryset)

    @detail_route(methods=['post'])
    def recalccharges(self, request, pk=None):
        apartment = Apartment.objects.get(pk=pk)
        return self.process_recalc_charges(request, apartment=apartment)


class ServiceViewSet(BaseModelViewSet):
    """
    API endpoint that allows services to be viewed or edited.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_superuser:
            return (IsAuthenticated(), )
        allowed_methods = ('GET', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )
        return (NoPermissions(), )

    def list(self, request):
        services = Service.objects.all()
        return self.list_paginated(request, services, ServiceSerializer)


class UnitViewSet(BaseModelViewSet):
    """
    API endpoint that allows units to be viewed.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_superuser:
            return (IsAuthenticated(), )
        return (NoPermissions(), )

    def list(self, request):
        services = Service.objects.all()
        return self.list_paginated(request, services, ServiceSerializer)


class AccountViewSet(BaseModelViewSet):
    """
    API endpoint that allows accounts to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_superuser:
            return (IsAuthenticated(), )
        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )
        return (NoPermissions(), )

    def list(self, request):
        if request.user.is_superuser:
            accounts = Account.objects.all()
        else:
            cooperative = request.user.cooperative
            accounts = Account.objects.filter(
                apartment__house__cooperative=cooperative)

        return self.list_paginated(request, accounts, AccountSerializer)

    def update(self, request, *args, **kwargs):
        account = get_object_or_404(Account, pk=kwargs.get('pk'))
        value = request.data.get('balance')
        if value:
            account.update_balance(value=value)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeterViewSet(BaseModelViewSet):
    """
    API endpoint that allows meter to be viewed or edited.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )

    @detail_route(methods=['get', 'post'])
    def indicators(self, request, pk):
        """
        Return the indicators of the meter or create a new indicator.
        """
        meter = Meter.objects.get(pk=pk)
        apartment_meter = ApartmentMeter.objects.get(meter=meter)
        user = request.user
        if not user.can_manage(apartment_meter.get_cooperative()):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            indicators = ApartmentMeterIndicator.objects.filter(
                meter=apartment_meter)
            context = {
                'request': request,
            }
            serializer = ApartmentMeterIndicatorSerializer(
                indicators, many=True, context=context)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = ApartmentMeterIndicatorSerializer(data=request.data)
            if serializer.is_valid():
                meter = ApartmentMeterIndicator(
                    meter=apartment_meter, **serializer.validated_data)
                meter.save()
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeterIndicatorViewSet(BaseModelViewSet):
    """
    API endpoint that allows apartment meter indicator to be viewed or
    edited.
    """
    queryset = MeterIndicator.objects.all()
    serializer_class = MeterIndicatorSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        if user.account:
            return (IsInhabitant(), )

        return (NoPermissions(), )

    def update(self, request, *args, **kwargs):
        data = request.data
        indicator = get_object_or_404(MeterIndicator, pk=kwargs.get('pk'))
        data = {
            'value': request.data.get('value'),
            'date': datetime.datetime.now().date(),
        }
        serializer = MeterIndicatorSerializer(
            indicator, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChargeViewSet(BaseModelViewSet):
    """
    API endpoint that allows charge to be viewed or edited.
    """
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )

    def list(self, request):
        user = request.user
        queryset = self.queryset.filter(
            account__apartment__house__cooperative=user.cooperative)
        return self.list_paginated(request, queryset, ChargeSerializer)

    def calc(self):
        pass


class UnitAPIView(APIView):
    """
    API endpoint that allows units to be viewed.
    """
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all units.
        """
        units = {}
        for item in UNITS:
            units[item[0]] = _(item[1])
        return Response({'data': units})


class UserViewSet(BaseModelViewSet):
    """
    API endpoint that allows user to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_superuser:
            return (IsAuthenticated(), )
        return (NoPermissions(), )

    def list(self, request):
        return self.list_paginated(request, self.queryset, UserSerializer)

    def create(self, request):
        if not request.user.is_superuser:
            return self._get_permission_denied_response()
        return super(UserViewSet, self).create(request)


class UserAPIView(APIView):
    """
    API endpoint that allows user's info to be viewed.
    """
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all units.
        """
        user = request.user
        resp = {
            'email': user.email,
            'manager': False,
            'superuser': False,
            'inhabitant': False,
            }
        cooperative = user.cooperative
        if cooperative:
            resp['cooperative_id'] = cooperative.id
            resp['cooperative_name'] = cooperative.name
            resp['manager'] = True
        elif user.is_superuser:
            resp['superuser'] = True
        elif user.account:
            resp['account_id'] = user.account.id
            resp['apartment_id'] = user.account.apartment.id
            resp['inhabitant'] = True
        return Response(resp)


class BreadcrumbAPIView(APIView):
    """
    API endpoint that allows breadcrumbs to be viewed.
    """
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all units.
        """
        def cooperative_label(cooperative, active=False):
            return {
                'label': cooperative.name,
                'active': active,
                'uri': '/#!/associations/{0}/'.format(cooperative.id),
                }

        def house_label(house, active=False):
            prefix = _('house')
            prefix = prefix[0].upper() + prefix[1:]
            return {
                'label': '{} {}'.format(
                    prefix, house.address.house.number),
                'active': active,
                'uri': '/#!/houses/{0}/'.format(house.id),
                }

        def apartment_label(house, active=False):
            prefix = _('apartment')
            prefix = prefix[0].upper() + prefix[1:]
            return {
                'label': '{} {}'.format(
                    prefix, apartment.address.apartment.number),
                'active': active,
                'uri': '/#!/apartments/{0}/'.format(apartment.id),
                }

        items = []
        params = request.query_params
        if params.get('association_id') and params.get('superuser') == 'true':
           hc = HousingCooperative.objects.get(pk=params.get('association_id'))
           return Response([cooperative_label(hc, True)])
        if (params.get('superuser') == 'true'
             or params.get('manager') == 'true'):
            if params.get('houseId'):
                house = House.objects.get(pk=params.get('houseId'))
                if params.get('superuser') == 'true':
                    items.append(cooperative_label(house.cooperative))
                items.append(house_label(house, True))
                return Response(items)
            if params.get('apartmentId'):
                apartment = Apartment.objects.get(pk=params.get('apartmentId'))
                if params.get('superuser') == 'true':
                    items.append(cooperative_label(apartment.house.cooperative))
                items.append(house_label(apartment.house))
                items.append(apartment_label(apartment, True))
                return Response(items)
        if params.get('inhabitant') == 'true' and params.get('apartmentId'):
            apartment = Apartment.objects.get(pk=params.get('apartmentId'))
            items.append(apartment_label(apartment, True))
            return Response(items)
        return Response({})


class BankAccountViewSet(BaseModelViewSet):
    """
    API endpoint that allows houses to be viewed or edited.
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_permissions(self):
        """
        Admin is granted to add/change/delete a bank account
        """
        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'PATCH', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from dateutil.relativedelta import relativedelta

from django.db import IntegrityError
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
    ApartmentMeter,
    ApartmentMeterIndicator,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService as HCService,
    Meter,
    Account,
    Service,
    UNITS,
)
from osbb.permissions import (
    IsManager,
    NoPermissions,
)
from osbb.serializers import (
    AccountSerializer,
    ApartmentSerializer,
    ApartmentMeterIndicatorSerializer,
    ChargeSerializer,
    HouseSerializer,
    HousingCooperativeSerializer as HCSerializer,
    HousingCooperativeServiceSerializer as HCServiceSerializer,
    MeterSerializer,
    ServiceSerializer,
)


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

    def list_paginated(self, request, queryset, serializer_class):
        order = request.query_params.get('order', 'name')
        limit = self.get_limit(request)
        offset = self.get_page(request) * limit
        limit = offset + limit
        qset = queryset.order_by(order).all()
        qset = qset[offset:limit]
        serializer = serializer_class(qset, many=True)
        data = {
            'data': serializer.data,
            'count': queryset.count(),
        }
        return Response(data)


class HousingCooperativeViewSet(BaseModelViewSet):
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

        if user.is_staff and self.request.method in ('PUT', 'GET', 'POST', ):
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
            serializer = HouseSerializer(data=request.data)
            if serializer.is_valid():
                house = House(
                    cooperative=cooperative, **serializer.validated_data)
                house.save()
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response({
                'status': 'Bad Request',
                'message': 'House could not be created with received data'
            }, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get', 'post', 'delete'])
    def services(self, request, pk):
        """
        Return the houses of the cooperative or create a new house.
        """
        cooperative = HousingCooperative.objects.get(pk=pk)
        user = request.user
        if not user.is_superuser:
            return self._get_permission_denied_response()
        if request.method == 'GET':
            hc_services = HCService.objects.filter(cooperative=pk)
            return self.list_paginated(
                request, hc_services, HCServiceSerializer)
        elif request.method == 'POST':
            data = request.data
            data['cooperative'] = cooperative.id
            service = Service.objects.get(pk=data.get('service'))
            serializer = HCServiceSerializer(data=data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                hc_service = HCService(
                    cooperative=cooperative, service=service, **validated_data)
                try:
                    hc_service.save()
                except IntegrityError:
                    message = _(
                        'For the given condominium service already exists')
                    return Response(
                        message, status=status.HTTP_400_BAD_REQUEST)
                response_data = {
                    'cooperative': cooperative.id,
                    'service': service.id,
                    'notes': validated_data.get('notes'),
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                hc_service_id = int(request.query_params.get('service_id'))
            except ValueError:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            hc_service = HCService.objects.get(pk=hc_service_id)
            hc_service.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def charge(self, request, pk=None):
        charges = []
        first_day = date.today().replace(day=1)
        previous_month = first_day - relativedelta(days=1)
        next_month = date.today() + relativedelta(months=1, day=1)
        last_day = next_month - relativedelta(days=1)
        cooperative = HousingCooperative.objects.get(pk=pk)
        accounts = Account.objects.filter(
            apartment__house__cooperative=cooperative)
        for account in accounts:
            apartment = account.apartment
            # import pdb
            # pdb.set_trace()
            meter = ApartmentMeter.objects.filter(apartment=apartment)[0]
            indicator_beginning = ApartmentMeterIndicator.objects.filter(
                meter=meter,
                date__year=previous_month.year,
                date__month=previous_month.month
                )[0]
            indicator_end = ApartmentMeterIndicator.objects.filter(
                meter=meter,
                date__year=first_day.year,
                date__month=first_day.month
                )[0]
            tariff = account.get_tariff()
            value = (indicator_end.value - indicator_beginning.value) * tariff
            charge = Charge(
                account=account,
                date=timezone.now().date(),
                start_date=first_day,
                end_date=last_day,
                tariff=account.get_tariff(),
                indicator_beginning=indicator_beginning.value,
                indicator_end=indicator_end.value,
                value=value
                )
            charges.append(charge)
        context = {
            'request': request,
        }
        serializer = ChargeSerializer(charges, many=True, context=context)
        for charge in charges:
            charge.save()
        return Response(serializer.data)
        # if serializer.is_valid():
        #     for charge in charges:
        #         charge.save()
        #     return Response(serializer.data)
        # else:
        #     return Response(
        #         serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            indicators = ApartmentMeterIndicator.objects.filter(
                meter__apartment__house__cooperative=cooperative)
            return self.list_paginated(
                request, indicators, ApartmentMeterIndicatorSerializer)


class HouseViewSet(BaseModelViewSet):
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

        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
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

    @detail_route(methods=['get', 'post'])
    def apartments(self, request, pk):
        """
        Return the apartments of the house or create a new apartment.
        """
        house = House.objects.get(pk=pk)
        user = request.user
        if not user.can_manage(house):
            return self._get_permission_denied_response()
        if request.method == 'GET':
            apartments = Apartment.objects.filter(house=pk)
            return self.list_paginated(
                request, apartments, ApartmentSerializer)
        elif request.method == 'POST':
            serializer = ApartmentSerializer(data=request.data)
            if serializer.is_valid():
                apartment = Apartment(house=house, **serializer.validated_data)
                apartment.save()
                account = Account(apartment=apartment)
                account.save()
                response_data = serializer.validated_data
                response_data['id'] = apartment.id
                return Response(
                    response_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApartmentViewSet(BaseModelViewSet):
    """
    API endpoint that allows apartments to be viewed or edited.
    """
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

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
        elif request.method == 'PUT':
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
        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
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

        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
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


class ApartmentMeterIndicatorViewSet(BaseModelViewSet):
    """
    API endpoint that allows apartment meter indicator to be viewed or
    edited.
    """
    queryset = ApartmentMeterIndicator.objects.all()
    serializer_class = ApartmentMeterIndicatorSerializer

    def get_permissions(self):

        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )


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

        allowed_methods = ('PUT', 'GET', 'POST', 'DELETE', )
        if user.is_staff and self.request.method in allowed_methods:
            return (IsManager(), )

        return (NoPermissions(), )


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
        cooperative = request.user.cooperative
        if request.user.cooperative:
            return Response({
                'cooperative_id': cooperative.id,
                'cooperative_name': cooperative.name,
            })

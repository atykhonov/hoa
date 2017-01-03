# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from osbb.models import (
    Apartment,
    ApartmentMeter,
    ApartmentMeterIndicator,
    House,
    HousingCooperative,
    HousingCooperativeService as HCService,
    Meter,
    Service,
)
from osbb.permissions import (
    IsManager,
    NoPermissions,
)
from osbb.serializers import (
    ApartmentSerializer,
    ApartmentMeterIndicatorSerializer,
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
        return super(HousingCooperativeViewSet, self).list(request)

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
            context = {
                'request': request,
            }
            serializer = HouseSerializer(houses, many=True, context=context)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = HouseSerializer(data=request.data)
            if serializer.is_valid():
                House(cooperative=cooperative, **serializer.validated_data)
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response({
                'status': 'Bad Request',
                'message': 'House could not be created with received data'
            }, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get', 'post'])
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
            context = {
                'request': request,
            }
            serializer = HCServiceSerializer(
                hc_services, many=True, context=context)
            return Response(serializer.data)
        elif request.method == 'POST':
            data = request.data
            data['cooperative'] = cooperative.id
            serializer = HCServiceSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                HCService(**validated_data)
                response_data = {
                    'cooperative': validated_data['cooperative'].id,
                    'service': validated_data['service'].id,
                    'notes': validated_data['notes'],
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            houses = House.objects.filter(cooperative=request.user.cooperative)

        page = self.paginate_queryset(houses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)

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
            context = {
                'request': request,
            }
            serializer = ApartmentSerializer(
                apartments, many=True, context=context)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = ApartmentSerializer(data=request.data)
            if serializer.is_valid():
                Apartment(house=house, **serializer.validated_data)
                return Response(
                    serializer.validated_data, status=status.HTTP_201_CREATED)

            return Response({
                'status': 'Bad Request',
                'message': 'House could not be created with received data'
            }, status=status.HTTP_400_BAD_REQUEST)


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

        page = self.paginate_queryset(apartments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApartmentSerializer(apartments, many=True)
        return Response(serializer.data)

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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from osbb.models import House, HousingCooperative
from osbb.permissions import (
    CooperativePermission,
    NoPermissions,
)
from osbb.serializers import HouseSerializer, HousingCooperativeSerializer


class HousingCooperativeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cooperatives to be viewed or edited.
    """
    queryset = HousingCooperative.objects.all()
    serializer_class = HousingCooperativeSerializer
    authentication_classes = (JSONWebTokenAuthentication, )

    def get_permissions(self):
        """
        Admin user is granted to add/change/delete a cooperative, but a
        manager is granted only to change it.
        """
        user = self.request.user

        if user.is_superuser:
            return (IsAuthenticated(), )

        if user.is_staff and self.request.method in ('PUT', 'GET', ):
            return (CooperativePermission(), )

        return (NoPermissions(), )

    def list(self, request):
        if request.user.is_staff:
            details = 'You do not have permission to perform this action.'
            return Response({
                'details': details,
                }, status=status.HTTP_403_FORBIDDEN)
        return super().list(request)


    # def get_queryset(self):
    #     queryset = HousingCooperative.objects.all()
    #     name = self.request.query_params.get('id', None)
    #     if name is not None:
    #         queryset = queryset.filter(id=id)

    #     return queryset
    # def create(self, request):
    #     serializer = self.serializer_class(data=request.data)

    #     if serializer.is_valid():
    #         HousingCooperative.objects.create_user(**serializer.validated_data)
    #         return Response(
    #             serializer.validated_data, status=status.HTTP_201_CREATED)

    #     return Response({
    #         'status': 'Bad Request',
    #         'message': 'Account could not be created with received data'
    #     }, status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def houses(self, request, pk):

        houses = House.objects.filter(housing_cooperative=pk)

        context = {
            'request': request,
        }

        serializer = HouseSerializer(houses, many=True, context=context)
        return Response(serializer.data)


class HouseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows houses to be viewed or edited.
    """
    queryset = House.objects.all()
    serializer_class = HouseSerializer

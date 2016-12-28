# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from osbb.models import House, HousingCooperative
from osbb.serializers import HouseSerializer, HousingCooperativeSerializer


class HousingCooperativeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cooperatives to be viewed or edited.
    """
    queryset = HousingCooperative.objects.all()
    serializer_class = HousingCooperativeSerializer

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

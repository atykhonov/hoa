# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from osbb.models import HousingCooperative
from osbb.serializers import HousingCooperativeSerializer


class HousingCooperativeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = HousingCooperative.objects.all()
    serializer_class = HousingCooperativeSerializer

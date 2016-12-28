# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from osbb.models import HousingCooperative


class HousingCooperativeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HousingCooperative
        fields = ('name', 'individual_tax_number', 'edrpou', 'certificate')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from osbb.models import House, HousingCooperative


class HouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = House
        fields = (
            'id',
            'name',
            'address',
        )


class HousingCooperativeSerializer(serializers.ModelSerializer):

    houses = HouseSerializer(many=True, read_only=True)

    class Meta:
        model = HousingCooperative
        fields = (
            'name',
            'individual_tax_number',
            'edrpou',
            'houses',
            'certificate',
        )

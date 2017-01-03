# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from osbb.models import (
    Apartment,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Service,
)


class HousingCooperativeServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = HousingCooperativeService
        fields = (
            'id',
            'cooperative',
            'service',
            'notes',
            )


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = (
            'id',
            'name',
            'unit',
            )


class ApartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Apartment
        fields = (
            'id',
            'number',
            'floor',
            'entrance',
            'room_number',
            'total_area',
            'dwelling_space',
            'heating_area',
            )


class HouseSerializer(serializers.ModelSerializer):

    apartments = ApartmentSerializer(many=True, read_only=True)

    class Meta:
        model = House
        fields = (
            'id',
            'name',
            'address',
            'apartments',
        )


class HousingCooperativeSerializer(serializers.ModelSerializer):

    houses = HouseSerializer(many=True, read_only=True)

    class Meta:
        model = HousingCooperative
        fields = (
            'id',
            'name',
            'individual_tax_number',
            'edrpou',
            'houses',
            'certificate',
            'legal_address',
            'physical_address',
            'phone_number',
            )

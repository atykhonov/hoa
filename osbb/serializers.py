# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from osbb.models import (
    Apartment,
    ApartmentMeter,
    ApartmentMeterIndicator,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    Service,
)


class ApartmentMeterIndicatorSerializer(serializers.ModelSerializer):

    class Meta:

        model = ApartmentMeterIndicator

        fields = (
            'date',
            'value',
        )


class MeterSerializer(serializers.ModelSerializer):

    indicators = ApartmentMeterIndicatorSerializer(many=True, read_only=True)

    class Meta:

        model = Meter

        fields = (
            'type',
            'number',
            'unit',
            'entry_date',
            'verification_date',
            'indicators',
            )


class ApartmentMeterSerializer(serializers.ModelSerializer):

    class Meta:

        model = ApartmentMeter

        fields = (
            'apartment',
            'meter',
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

    meters = ApartmentMeterSerializer(many=True, read_only=True)

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
            'meters',
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

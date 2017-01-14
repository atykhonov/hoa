# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from rest_framework import serializers

from osbb.models import (
    Apartment,
    ApartmentMeter,
    ApartmentMeterIndicator,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    Account,
    Service,
    User,
    UNITS,
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = (
            'id',
            'first_name',
            'last_name',
        )


class ChargeSerializer(serializers.ModelSerializer):

    class Meta:

        model = Charge

        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):

    class Meta:

        model = Account

        fields = (
            'uid',
            'apartment',
            'owner',
            'first_name',
            'last_name',
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


class ServiceSerializer(serializers.ModelSerializer):

    unit_translated = serializers.SerializerMethodField()

    class Meta:

        model = Service

        fields = (
            'id',
            'name',
            'unit',
            'unit_translated',
            )

    def get_unit_translated(self, obj):
        for unit in UNITS:
            if unit[0] == obj.unit:
                return _(unit[1])


class HousingCooperativeServiceSerializer(serializers.ModelSerializer):

    service = ServiceSerializer(read_only=True)

    class Meta:

        model = HousingCooperativeService

        fields = (
            'id',
            'cooperative',
            'service',
            'notes',
            )
        depth = 1


class ApartmentSerializer(serializers.ModelSerializer):

    meters = ApartmentMeterSerializer(many=True, read_only=True)

    account = AccountSerializer(read_only=True)

    class Meta:

        model = Apartment

        fields = (
            'id',
            'house',
            'number',
            'floor',
            'entrance',
            'room_number',
            'total_area',
            'dwelling_space',
            'heating_area',
            'meters',
            'tariff',
            'account',
            )

        depth = 1


class HouseSerializer(serializers.ModelSerializer):

    apartments = ApartmentSerializer(many=True, read_only=True)

    cooperative = serializers.PrimaryKeyRelatedField(
        queryset=HousingCooperative.objects.all())

    address = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = (
            'id',
            'cooperative',
            'address',
            'street',
            'number',
            'apartments',
            'tariff',
            'apartments_count',
            )

        depth = 2

    def get_address(self, obj):
        if obj.street and obj.number:
            return '{}, {}'.format(obj.street, obj.number)
        return ''

    def create(self, validated_data):
        house = House.objects.create(**validated_data)
        house.save()
        if house.apartments_count:
            for n in range(house.apartments_count):
                apartment = Apartment.objects.create(house=house, number=n+1)
                apartment.save()
        return house


class HousingCooperativeSerializer(serializers.ModelSerializer):

    houses = HouseSerializer(many=True, read_only=True)

    manager = UserSerializer(read_only=True)

    services = HousingCooperativeServiceSerializer(many=True, read_only=True)

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
            'manager',
            'houses_count',
            'services',
            )

    def create(self, validated_data):
        cooperative = HousingCooperative.objects.create(**validated_data)
        cooperative.save()
        service = Service.objects.get(required=True)
        hc_service = HousingCooperativeService.objects.create(
            cooperative=cooperative, service=service)
        hc_service.save()
        return cooperative

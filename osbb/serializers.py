# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

    account = AccountSerializer(read_only=True)

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
            'tariff',
            'account',
            )

    # def create(self, validated_data):
    #     profile_data = validated_data.pop('profile')
    #     user = User.objects.create(**validated_data)
    #     Profile.objects.create(user=user, **profile_data)
    #     return user


class HouseSerializer(serializers.ModelSerializer):

    apartments = ApartmentSerializer(many=True, read_only=True)

    class Meta:
        model = House
        fields = (
            'id',
            'cooperative',
            'name',
            'address',
            'apartments',
            'tariff',
            'apartments_count',
            )
        depth = 1


class HousingCooperativeSerializer(serializers.ModelSerializer):

    houses = HouseSerializer(many=True, read_only=True)

    manager = UserSerializer(read_only=True)

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
            )

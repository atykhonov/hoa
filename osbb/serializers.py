# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from rest_framework import serializers

from osbb.models import (
    Apartment,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    MeterIndicator,
    Account,
    Service,
    ServiceCharge,
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


class ServiceChargeSerializer(serializers.ModelSerializer):

    class Meta:

        model = ServiceCharge

        fields = '__all__'

        depth = 1


class ChargeSerializer(serializers.ModelSerializer):

    services = ServiceChargeSerializer(many=True, read_only=True)

    address = serializers.SerializerMethodField()

    class Meta:

        model = Charge

        fields = (
            'id',
            'account',
            'address',
            'period',
            'services',
            'total',
        )

        depth = 2

    def get_address(self, obj):
        """
        Return the address of the account to which the charge belongs
        to.
        """
        apartment = obj.account.apartment
        house = apartment.house
        return '{} {} {}, {}'.format(
            _('str.'), house.street, house.number, apartment.number)


class AccountSerializer(serializers.ModelSerializer):

    class Meta:

        model = Account

        fields = (
            'id',
            'uid',
            'apartment',
            'owner',
            'first_name',
            'last_name',
            )


class MeterIndicatorSerializer(serializers.ModelSerializer):

    account = serializers.SerializerMethodField()

    address = serializers.SerializerMethodField()

    class Meta:

        model = MeterIndicator

        fields = (
            'id',
            'account',
            'address',
            'date',
            'meter',
            'period',
            'value',
            )

        depth = 3

    def get_account(self, obj):
        """Return the account to which the meter belongs to."""
        return AccountSerializer(obj.meter.apartment.account).data

    def get_address(self, obj):
        """
        Return the address of the account to which the meter belongs to.
        """
        apartment = obj.meter.apartment
        house = apartment.house
        return '{} {} {}, {}'.format(
            _('str.'), house.street, house.number, apartment.number)


class MeterSerializer(serializers.ModelSerializer):

    indicators = MeterIndicatorSerializer(many=True, read_only=True)

    class Meta:

        model = Meter

        fields = (
            'number',
            'entry_date',
            'verification_date',
            'indicators',
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

    meters = MeterSerializer(many=True, read_only=True)

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
        coop_services = house.cooperative.services.filter(
            service__requires_meter=True)
        if house.apartments_count:
            for n in range(house.apartments_count):
                apartment = Apartment.objects.create(house=house, number=n+1)
                apartment.save()
                for coop_service in coop_services:
                    meter = Meter(
                        apartment=apartment, service=coop_service.service)
                    meter.save()
                account = Account(apartment=apartment)
                account.save()
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

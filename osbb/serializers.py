# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from rest_framework import serializers

from address.models import Address
from address.serializers import AddressSerializer
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

    full_name = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            )

    def get_full_name(self, instance):
        if instance.first_name and instance.last_name:
            return '{0} {1}'.format(instance.first_name, instance.last_name)
        elif instance.first_name:
            return instance.first_name
        elif instance.last_name:
            return instance.last_name
        return ''


class ServiceChargeSerializer(serializers.ModelSerializer):

    class Meta:

        model = ServiceCharge

        fields = '__all__'

        depth = 1


class ChargeSerializer(serializers.ModelSerializer):

    services = ServiceChargeSerializer(many=True, read_only=True)

    address = serializers.SerializerMethodField()

    pid = serializers.SerializerMethodField()

    class Meta:

        model = Charge

        fields = (
            'id',
            'pid',
            'account',
            'address',
            'period',
            'services',
            'total',
        )

        depth = 2

    def get_address(self, instance):
        """
        Return the address of the account to which the charge belongs
        to.
        """
        return instance.account.apartment.address.medium()

    def get_pid(self, instance):
        """
        Return personal account number.
        """
        return instance.account.get_pid()


class AccountSerializer(serializers.ModelSerializer):

    pid = serializers.SerializerMethodField()

    address = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()

    class Meta:

        model = Account

        fields = (
            'id',
            'pid',
            'apartment',
            'owner',
            'first_name',
            'last_name',
            'full_name',
            'address',
            )

    def get_pid(self, instance):
        return instance.get_pid()

    def get_address(self, instance):
        """
        Return the address of the account.
        """
        return instance.apartment.address.medium()

    def get_full_name(self, instance):
        if instance.first_name and instance.last_name:
            return '{0} {1}'.format(instance.last_name, instance.first_name)
        elif instance.first_name:
            return instance.first_name
        elif instance.last_name:
            return instance.last_name
        return ''


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
        return obj.meter.apartment.address.medium()


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
            'required',
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

    address = AddressSerializer(read_only=True)

    number = serializers.CharField(write_only=True)

    class Meta:

        model = Apartment

        fields = (
            'id',
            'address',
            'number',
            'house',
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

    address = AddressSerializer(read_only=True)

    street = serializers.CharField(write_only=True, required=False)

    number = serializers.CharField(write_only=True, required=False)

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

    def get_street(self, obj):
        return obj.address.street.name

    def get_number(self, obj):
        return obj.address.house.number

    def create(self, validated_data):
        """
        Create a house with data taken from the given
        `validated_data`.
        """
        msg = None
        street_name = validated_data.pop('street', '')
        if not street_name:
            msg = 'Street field is required.'
        house_number = validated_data.pop('number', '')
        if not house_number:
            msg = 'House number field is required.'
        if msg:
            raise serializers.ValidationError(msg)

        address = Address.objects.create_address(street_name, house_number)

        house = House.objects.create(address=address, **validated_data)
        house.save()

        coop_services = house.cooperative.services.filter(
            service__requires_meter=True)
        if house.apartments_count:
            for n in range(house.apartments_count):
                address = Address.objects.create_address(
                    street_name, house_number, n+1)
                apartment = Apartment.objects.create(
                    house=house, address=address)
                for coop_service in coop_services:
                    meter = Meter.objects.create(
                        apartment=apartment, service=coop_service.service)
                    meter.create_indicators()
                account = Account.objects.create(apartment=apartment)
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

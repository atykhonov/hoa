# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers

from address.models import Address
from address.serializers import AddressSerializer
from osbb.models import (
    Account,
    AccountBalance,
    Apartment,
    BankAccount,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    MeterIndicator,
    Service,
    ServiceCharge,
    User,
    UNITS,
)


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()

    last_name = serializers.CharField()

    is_superuser = serializers.NullBooleanField(default=False)

    cooperative = serializers.PrimaryKeyRelatedField(
        default=None, queryset=HousingCooperative.objects.all())

    class Meta:

        model = get_user_model()

        fields = (
            'id',
            'email',
            'password',
            'is_superuser',
            'first_name',
            'last_name',
            'full_name',
            'cooperative',
            )

        extra_kwargs = {
            'password': {
                'write_only': True,
                },
            }

    def get_full_name(self, instance):
        if instance.first_name and instance.last_name:
            return '{0} {1}'.format(instance.first_name, instance.last_name)
        elif instance.first_name:
            return instance.first_name
        elif instance.last_name:
            return instance.last_name
        return ''

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_superuser=validated_data['is_superuser'],
            cooperative=validated_data.get('cooperative')
        )
        user.set_password(validated_data['password'])
        if user.cooperative:
            user.is_staff = True
        user.save()
        return user


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
            # 'period',
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


class AccountBalanceSerializer(serializers.ModelSerializer):

    class Meta:

        model = AccountBalance

        fields = (
            'id',
            'account',
            'period',
            'value',
            )


class AccountSerializer(serializers.ModelSerializer):

    pid = serializers.SerializerMethodField()

    address = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()

    balance = serializers.SerializerMethodField()

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
            'balance',
            )

        depth = 3

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

    def get_balance(self, instance):
        """
        Get balance of the account.
        """
        balance = instance.get_present_balance()
        if not balance:
            balance = instance.get_previous_balance()
            if not balance:
                return Decimal(0)
        return balance.value


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

        depth = 4

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
            'tariff',
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
                account.create_balance()
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


class BankAccountSerializer(serializers.ModelSerializer):

    cooperative = serializers.PrimaryKeyRelatedField(
        queryset=HousingCooperative.objects.all())

    class Meta:
        model = BankAccount
        fields = (
            'id',
            'cooperative',
            'mfo',
            'name',
            'address',
            )

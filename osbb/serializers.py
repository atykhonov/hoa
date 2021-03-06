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
    ApartmentTariff,
    BankAccount,
    Charge,
    House,
    HousingCooperative,
    HousingCooperativeService,
    HouseTariff,
    Meter,
    MeterIndicator,
    Service,
    ServiceCharge,
    User,
    UNITS,
)


class AccountSerializer(serializers.ModelSerializer):

    pid = serializers.SerializerMethodField()

    address = serializers.SerializerMethodField()

    full_name = serializers.SerializerMethodField()

    balance = serializers.SerializerMethodField()

    amount = serializers.IntegerField(write_only=True)

    comment = serializers.CharField(write_only=True)

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
            'amount',
            'comment',
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
        return instance.get_balance()

    def update(self, instance, validated_data):
        amount = validated_data.pop('amount', None)
        if amount:
            comment = validated_data.pop('comment', None)
            if not comment:
                raise serializers.ValidationError(
                    'Field "comment" is required.')
            instance.override_balance(amount, comment)
        return instance


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()

    last_name = serializers.CharField()

    is_superuser = serializers.NullBooleanField(default=False)

    is_staff = serializers.NullBooleanField(default=False)

    cooperative = serializers.PrimaryKeyRelatedField(
        default=None, queryset=HousingCooperative.objects.all())

    account = serializers.PrimaryKeyRelatedField(
        default=None, queryset=Account.objects.all())

    class Meta:

        model = get_user_model()

        fields = (
            'id',
            'email',
            'password',
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'full_name',
            'cooperative',
            'account',
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
            cooperative=validated_data.get('cooperative'),
            account=validated_data.get('account')
        )
        user.set_password(validated_data['password'])
        if user.cooperative:
            user.is_staff = True
        user.save()
        if validated_data.get('account') and user.account:
            user.account.owner = user
            user.account.save()
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

    id = serializers.IntegerField()

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

    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all())

    meters = MeterSerializer(many=True, read_only=True)

    account = AccountSerializer(read_only=True)

    address = AddressSerializer(read_only=True)

    number = serializers.IntegerField(write_only=True, required=False)

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
            'account',
            )

        depth = 1

    def create(self, validated_data):
        """
        Create an apartment with the data taken from `validated_data`.
        """
        apartment_number = validated_data.pop('number', '')
        if not apartment_number:
            raise serializers.ValidationError('Field "number" is required.')

        house = validated_data.get('house')
        address = Address.objects.create_apartment_address(
            house.address, apartment_number)

        apartment = Apartment.objects.create(address=address, **validated_data)

        account = Account.objects.create(apartment=apartment)

        coop_services = house.cooperative.services.all()
        for coop_service in coop_services:
            ApartmentTariff.objects.create(
                apartment=apartment, service=coop_service.service)
            if coop_service.service.requires_meter:
                meter = Meter.objects.create(
                    apartment=apartment, service=coop_service.service)
                meter.create_indicators()

        return apartment


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

        address = Address.objects.create_house_address(
            street_name, house_number)

        house = House.objects.create(address=address, **validated_data)

        coop_services = house.cooperative.services.all()
        for coop_service in coop_services:
            HouseTariff.objects.create(
                house=house, service=coop_service.service)

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


class HouseTariffSerializer(serializers.ModelSerializer):

    house = HouseSerializer()

    service = ServiceSerializer()

    class Meta:

        model = HouseTariff

        fields = (
            'id',
            'house',
            'service',
            'tariff',
            )


class ApartmentTariffSerializer(serializers.ModelSerializer):

    apartment = ApartmentSerializer(read_only=True)

    service = ServiceSerializer(read_only=True)

    class Meta:

        model = ApartmentTariff

        fields = (
            'id',
            'apartment',
            'service',
            'tariff',
            )

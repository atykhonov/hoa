# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from address.models import Address, Apartment, City, House, Street


class CitySerializer(serializers.ModelSerializer):

    class Meta:

        model = City

        fields = (
            'name',
        )


class StreetSerializer(serializers.ModelSerializer):

    city = CitySerializer()

    name = serializers.CharField()

    class Meta:

        model = Street

        fields = (
            'city',
            'name',
            'type',
        )


class HouseSerializer(serializers.ModelSerializer):

    street = StreetSerializer()

    number = serializers.IntegerField()

    class Meta:

        model = House

        fields = (
            'street',
            'number',
            'index',
        )


class ApartmentSerializer(serializers.ModelSerializer):

    house = HouseSerializer()

    class Meta:

        model = Apartment

        fields = (
            'house',
            'number',
            'index',
        )


class AddressSerializer(serializers.ModelSerializer):

    medium = serializers.SerializerMethodField()

    city = CitySerializer()

    street = StreetSerializer()

    house = HouseSerializer()

    apartment = ApartmentSerializer()

    class Meta:

        model = Address

        fields = (
            'id',
            'city',
            'street',
            'house',
            'apartment',
            'medium',
            )

        depth = 1

    def get_medium(self, obj):
        return obj.medium()

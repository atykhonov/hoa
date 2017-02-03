# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from address.models import Address


class AddressSerializer(serializers.ModelSerializer):

    medium = serializers.SerializerMethodField()

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

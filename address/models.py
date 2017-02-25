# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _

from core.models import BaseModel


STREET_TYPES = (
    ('ST', 'Street'),
    ('LN', 'Lane'),
    ('AV', 'Avenue'),
    ('BL', 'Boulevard'),
    ('SQ', 'Square'),
)

STREET_TYPE_SHORT = {
    'ST': 'st',
    'LN': 'ln',
    'AV': 'ave',
    'BL': 'blvd',
    'SQ': 'sq',
}

DEFAULT_STREET_TYPE = STREET_TYPES[0][0]

DEFAULT_CITY_NAME = 'Львів'


class City(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    @staticmethod
    def get_default_city():
        """
        Return default city. Currently 'Lviv' city is only supported. So,
        this is the default city.
        """
        lviv = City.objects.filter(name=DEFAULT_CITY_NAME)
        return lviv[0]


class Street(BaseModel):
    city = models.ForeignKey(City, related_name='streets')
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=2, choices=STREET_TYPES)

    class Meta:
        unique_together = (('city', 'name', 'type', ), )

    @staticmethod
    def get_default_type():
        """
        Return default street type.
        """
        return DEFAULT_STREET_TYPE


class House(BaseModel):
    street = models.ForeignKey(Street, related_name='houses')
    number = models.IntegerField()
    index = models.CharField(max_length=1)

    class Meta:
        unique_together = (('street', 'number', 'index', ), )


class Apartment(BaseModel):
    house = models.ForeignKey(House, related_name='apartments')
    number = models.IntegerField()
    index = models.CharField(max_length=1)

    class Meta:
        unique_together = (('house', 'number', 'index', ), )


class AddressManager(models.Manager):

    def create_house_address(self, street, house):
        """
        Create the address with the given street name and house
        number.
        """
        city = City.get_default_city()
        street_type = Street.get_default_type()
        try:
            street_obj = Street.objects.get(
                city=city, name=street, type=street_type)
        except Street.DoesNotExist:            
            street_obj = Street.objects.create(
                city=city, name=street, type=street_type)
        try:
            house_obj = House.objects.get(street=street_obj, number=house)
        except House.DoesNotExist:
            house_obj = House.objects.create(street=street_obj, number=house)
        address = self.create(
            city=city,
            street=street_obj,
            house=house_obj,
            )
        return address

    def create_apartment_address(self, house_address, apartment_number):
        """
        Create apartment address based on the given `house_address` with
        the given `apartment_number`.
        """
        try:
            apartment = Apartment.objects.get(
                house=house_address.house, number=apartment_number)
        except Apartment.DoesNotExist:
            apartment = Apartment.objects.create(
                house=house_address.house, number=apartment_number)
        return self.create(
            city=house_address.city,
            street=house_address.street,
            house=house_address.house,
            apartment=apartment,
            )


class Address(BaseModel):
    city = models.ForeignKey(City)
    street = models.ForeignKey(Street)
    house = models.ForeignKey(House)
    apartment = models.ForeignKey(Apartment, null=True)

    objects = AddressManager()

    class Meta:
        unique_together = (('city', 'street', 'house', 'apartment', ), )

    def __str__(self):
        street = self.street
        str_type = _(STREET_TYPE_SHORT[street.type])
        fmt = '{0}. {1}, {2}. {3}'
        if self.apartment:
            fmt += ', {4}. {5}'
            return fmt.format(
                str_type,
                street.name,
                _('hs'),
                self.house.number,
                _('apt'),
                self.apartment.number
                )
        return fmt.format(str_type, street.name, _('hs'), self.house.number)

    def medium(self):
        """
        Return medium size string representation of the address.
        """
        return str(self)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from core.models import BaseModel
from address import models
from address.models import Address, Apartment, City, House, Street


class CityTestCase(TestCase):

    def test_get_default_city(self):
        """
        The default city does exist and is ready to be used.
        """
        default_city = City.get_default_city()

        self.assertEquals(models.DEFAULT_CITY_NAME, default_city.name)


class StreetTestCase(TestCase):

    def test_get_default_type(self):
        """
        The default street type is returned.
        """
        default_street_type = Street.get_default_type()

        self.assertEquals(models.DEFAULT_STREET_TYPE, default_street_type)

    def test_save_with_default_type(self):
        """
        The street is saved with the default street type.
        """
        default_street_type = Street.get_default_type()
        city = City.get_default_city()
        street = Street(city=city, name='korotka', type=default_street_type)

        street.save()

        self.assertEquals(default_street_type, street.type)


class AddressTestCase(TestCase):

    def test_str_empty_apartment(self):
        """
        An address without apartment is represented as a string in the
        form of 'вул. Городоцька 17'.
        """
        city = City(name='Львів')
        street = Street(city=city, name='Городоцька', type='Street')
        house = House(number=17)
        address = Address(city=city, street=street, house=house)

        result = str(address)

        self.assertEquals('вул. Городоцька 17', result)

    def test_str_with_apartment(self):
        """
        An address with apartment is represented as a string in the form
        of 'вул. Городоцька 17, кв. 33'.
        """
        city = City(name='Львів')
        street = Street(city=city, name='Городоцька', type='Street')
        house = House(number=17)
        apartment = Apartment(number=33)
        address = Address(
            city=city, street=street, house=house, apartment=apartment)

        result = str(address)

        self.assertEquals('вул. Городоцька 17, кв. 33', result)

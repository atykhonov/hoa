# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import (
    Apartment,
    ApartmentMeter,
    Meter,
    House,
    HousingCooperative,
)


class ApartmentMeterTestCase(TestCase):

    def test_apartment_meter_creation(self):
        """
        Apartment meter is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(housing_cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=20)
        apartment.save()
        meter = Meter()
        meter.save()
        apartment_meter = ApartmentMeter(apartment=apartment, meter=meter)
        apartment_meter.save()

        self.assertEqual(apartment_meter.apartment.id, apartment.id)
        self.assertEqual(apartment_meter.meter.id, meter.id)

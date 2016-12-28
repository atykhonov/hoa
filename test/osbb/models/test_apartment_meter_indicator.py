# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone

from osbb.models import (
    Apartment,
    ApartmentMeter,
    ApartmentMeterIndicator,
    Meter,
    House,
    HousingCooperative,
)


class ApartmentMeterTestCase(TestCase):

    def test_apartment_meter_creation(self):
        """
        Apartment meter is created with certain attributes.
        """
        now = timezone.now()
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
        meter_indicator = ApartmentMeterIndicator(
            apartment_meter=apartment_meter, date=now, value=20)
        meter_indicator.save()

        self.assertEqual(
            apartment_meter.id, meter_indicator.apartment_meter.id)
        self.assertEqual(now, meter_indicator.date)
        self.assertEqual(20, meter_indicator.value)

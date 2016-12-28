# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone

from osbb.models import (
    Apartment,
    ApartmentTariff,
    House,
    HousingCooperative,
    Service,
)


class ApartmentTariffTestCase(TestCase):

    def test_apartment_tariff_creation(self):
        """
        Apartment tariff is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(housing_cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=10)
        apartment.save()
        service = Service()
        service.save()
        date = timezone.now()
        tariff = ApartmentTariff(
            apartment=apartment,
            deleted=False,
            date=date,
            service=service,
            value=20,
        )

        tariff.save()

        self.assertEqual(apartment.id, tariff.apartment.id)
        self.assertEqual(date, tariff.date)
        self.assertEqual(False, tariff.deleted)
        self.assertEqual(service.id, tariff.service.id)
        self.assertEqual(20, tariff.value)

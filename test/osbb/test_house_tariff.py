# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone

from osbb.models import (
    House,
    HouseTariff,
    HousingCooperative,
    Service,
)


class HouseTariffTestCase(TestCase):

    def test_house_tariff_creation(self):
        """
        House tariff is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(housing_cooperative=cooperative)
        house.save()
        service = Service()
        service.save()
        date = timezone.now()
        tariff = HouseTariff(
            house=house,
            date=date,
            service=service,
            value=20,
        )

        tariff.save()

        self.assertEqual(house.id, tariff.house.id)
        self.assertEqual(date, tariff.date)
        self.assertEqual(service.id, tariff.service.id)
        self.assertEqual(20, tariff.value)

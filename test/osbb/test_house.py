# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import House, HousingCooperative


class HouseTestCase(TestCase):

    def test_house_creation(self):
        """
        House is created with certain attributes.
        """
        name = 'house'
        address = 'wide str. 22, 33'
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(
            housing_cooperative=cooperative, name=name, address=address)

        house.save()

        self.assertEqual(cooperative.id, house.housing_cooperative.id)
        self.assertEqual(name, house.name)
        self.assertEqual(address, house.address)

# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import Apartment, House, HousingCooperative


class ApartmentTestCase(TestCase):

    def test_apartment_creation(self):
        """
        Apartment is created with certain attributes.
        """
        number = 22
        floor = 11
        entrance = 1
        room_number = 3
        total_area = 40
        dwelling_space = 30
        heating_area = 30
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(housing_cooperative=cooperative)
        house.save()
        apartment = Apartment(
            house=house,
            number=number,
            floor=floor,
            entrance=entrance,
            room_number=room_number,
            total_area=total_area,
            dwelling_space=dwelling_space,
            heating_area=heating_area,
        )

        apartment.save()

        self.assertEqual(house.id, apartment.house.id)
        self.assertEqual(number, apartment.number)
        self.assertEqual(floor, apartment.floor)
        self.assertEqual(entrance, apartment.entrance)
        self.assertEqual(room_number, apartment.room_number)
        self.assertEqual(total_area, apartment.total_area)
        self.assertEqual(dwelling_space, apartment.dwelling_space)
        self.assertEqual(heating_area, apartment.heating_area)

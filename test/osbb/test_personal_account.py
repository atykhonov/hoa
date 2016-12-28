# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import Apartment, House, HousingCooperative, PersonalAccount


class PersonalAccountTestCase(TestCase):

    def test_personal_account_creation(self):
        """
        Personal account is created with certain attributes.
        """
        uid = '000102030'
        prefix = '0001'
        receipt_text = 'text'
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(housing_cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=10)
        apartment.save()
        personal_account = PersonalAccount(
            apartment=apartment,
            uid=uid,
            prefix=prefix,
            receipt_text=receipt_text,
        )

        personal_account.save()

        self.assertEqual(apartment.id, personal_account.apartment.id)
        self.assertEqual(uid, personal_account.uid)
        self.assertEqual(prefix, personal_account.prefix)
        self.assertEqual(receipt_text, personal_account.receipt_text)

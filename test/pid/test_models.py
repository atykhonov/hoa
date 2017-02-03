# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from core.models import BaseModel
from pid.models import City


class CityPidTestCase(TestCase):

    def test_pid(self):
        """
        Test that pid contains id and padded with zeros.
        """
        city = City()
        city.save()

        self.assertEquals(1, city.id)
        self.assertEquals('001', city.get_pid())

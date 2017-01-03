# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import date
from dateutil.relativedelta import relativedelta

from autofixture import AutoFixture
from django.urls import reverse
from rest_framework import status

from osbb.models import (
    ApartmentMeter,
    ApartmentMeterIndicator,
    House,
    HousingCooperative,
    Meter,
    PersonalAccount,
)
from test.osbb.testcase import BaseAPITestCase


class TestCharge(BaseAPITestCase):

    def create_indicators(self, apartment, old, recent):
        first_day = date.today().replace(day=1)
        previous_month = first_day - relativedelta(months=1)

        meter1 = Meter()
        meter1.save()

        apartment_meter = ApartmentMeter(apartment=apartment, meter=meter1)
        apartment_meter.save()

        indicator_date = previous_month + relativedelta(days=10)
        meter_indicator1 = ApartmentMeterIndicator(
            meter=apartment_meter,
            date=indicator_date,
            value=old
        )
        meter_indicator1.save()

        indicator_date = first_day + relativedelta(days=10)
        meter_indicator2 = ApartmentMeterIndicator(
            meter=apartment_meter,
            date=indicator_date,
            value=recent
        )
        meter_indicator2.save()

    def test_change(self):
        """
        Test charge.
        """
        self.house1.tariff = 10000
        self.house1.save()

        self.create_indicators(self.apartment1, 20, 30)
        self.create_indicators(self.apartment2, 40, 50)
        self.create_indicators(self.apartment3, 60, 70)

        pa1 = PersonalAccount(apartment=self.apartment1)
        pa1.save()
        pa2 = PersonalAccount(apartment=self.apartment2)
        pa2.save()
        pa3 = PersonalAccount(apartment=self.apartment3)
        pa3.save()

        url = reverse(
            'cooperative-charge', kwargs={'pk': self.cooperative1.id})
        response = self.cpost(url, self.admin, {})

        response_content = json.loads(response.content.decode('utf-8'))

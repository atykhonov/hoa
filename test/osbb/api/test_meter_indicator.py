# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from osbb.models import ApartmentMeter, ApartmentMeterIndicator, Meter
from test.osbb.testcase import BaseAPITestCase


class BaseTestMeterIndicator(BaseAPITestCase):

    def create_fixtures(self, apartment):
        meter_fixture = AutoFixture(Meter)
        self.meter = meter_fixture.create(1)[0]
        apartment_meter_fixture = AutoFixture(
            ApartmentMeter,
            field_values={
                'apartment': apartment,
                'meter': self.meter,
            }
        )
        self.apartment_meter = apartment_meter_fixture.create(1)[0]
        self.meter_indicator_fixture = AutoFixture(
            ApartmentMeterIndicator,
            field_values={
                'meter': self.apartment_meter,
            }
        )
        self.meter_indicator = self.meter_indicator_fixture.create(1)[0]


class TestMeterIndicatorByManager(BaseTestMeterIndicator):

    def setUp(self):
        super(TestMeterIndicatorByManager, self).setUp()
        self.create_fixtures(self.apartment5)

    def test_creation(self):
        """
        The meter indicator is created by admin.
        """
        url = reverse('meter-indicators', kwargs={'pk': self.meter.id})

        data = {
            'date': timezone.now().strftime("%Y-%m-%d"),
            'value': '2468',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_updating(self):
        """
        The meter indicator is successfully updated.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        data = {
            'date': timezone.now().strftime("%Y-%m-%d"),
            'value': '6420',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_deleting(self):
        """
        The meter indicator is successfully deleted.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieving_item(self):
        """
        The meter indicator is successfully retrieved.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieving_list(self):
        """
        The meter indicators are successfully retrieved.
        """
        meter_indicator = self.meter_indicator_fixture.create(1)[0]

        url = reverse('meter-indicators', kwargs={'pk': self.meter.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class TestMeterIndicatorByManagerOfCooperative(BaseTestMeterIndicator):

    def setUp(self):
        super(TestMeterIndicatorByManagerOfCooperative, self).setUp()
        self.create_fixtures(self.apartment1)

    def test_creation(self):
        """
        The meter indicator is created by admin.
        """
        url = reverse('meter-indicators', kwargs={'pk': self.meter.id})

        data = {
            'date': timezone.now().strftime("%Y-%m-%d"),
            'value': '2468',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(
            ApartmentMeterIndicator.objects.filter(value=2468).exists())

    def test_updating(self):
        """
        The meter indicator is successfully updated.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        data = {
            'date': timezone.now().strftime("%Y-%m-%d"),
            'value': '6420',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(
            ApartmentMeterIndicator.objects.filter(value=6420).exists())

    def test_deleting(self):
        """
        The meter indicator is successfully deleted.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        q = ApartmentMeterIndicator.objects.filter(pk=self.meter_indicator.id)
        self.assertFalse(q.exists())

    def test_retrieving_item(self):
        """
        The meter indicator is successfully retrieved.
        """
        url = reverse(
            'meter-indicator-detail', kwargs={'pk': self.meter_indicator.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.meter_indicator.value, response.data['value'])
        self.assertEqual(
            self.meter_indicator.date.strftime("%Y-%m-%d"),
            response.data['date']
            )

    def test_retrieving_list(self):
        """
        The meter indicators are successfully retrieved.
        """
        meter_indicator = self.meter_indicator_fixture.create(1)[0]

        url = reverse('meter-indicators', kwargs={'pk': self.meter.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(2, len(response.data))
        self.assertEqual(self.meter_indicator.value, response.data[0]['value'])
        self.assertEqual(meter_indicator.value, response.data[1]['value'])

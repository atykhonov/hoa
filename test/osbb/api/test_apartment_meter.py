# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
import json

from osbb.models import ApartmentMeter, Meter, METER_TYPES, UNITS
from test.osbb.testcase import BaseAPITestCase


class TestApartmentMeterByAdmin(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment meter is created by admin.
        """
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        data = {
            'type': METER_TYPES[0][0],
            'number': '12345',
            'unit': UNITS[0][0],
            }
        response = self.cpost(url, self.admin, data)

        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        ameters = ApartmentMeter.objects.filter(apartment=self.apartment1)
        self.assertTrue(ameters.exists())
        ameter = ameters[0]
        self.assertTrue(ameter.apartment.id, self.apartment1.id)
        meter = ameter.meter
        self.assertTrue(METER_TYPES[0][0], meter.type)
        self.assertTrue('12345', meter.number)
        self.assertTrue(UNITS[0][0], meter.unit)

    def test_retrieving_list(self):
        """
        The apartment meters are successfully retrieved.
        """
        meter1 = Meter(type=METER_TYPES[0][0], number='1234', unit=UNITS[0][0])
        meter1.save()
        meter2 = Meter(type=METER_TYPES[0][1], number='4567', unit=UNITS[0][1])
        meter2.save()
        apartment_meter1 = ApartmentMeter(
            apartment=self.apartment1, meter=meter1)
        apartment_meter1.save()
        apartment_meter2 = ApartmentMeter(
            apartment=self.apartment1, meter=meter2)
        apartment_meter2.save()

        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(meter1.type, response_content[0]['type'])
        self.assertEqual('Heating', meter1.get_type_display())
        self.assertEqual(meter1.number, response_content[0]['number'])
        self.assertEqual(meter1.unit, response_content[0]['unit'])
        self.assertEqual('Square meters', meter1.get_unit_display())
        self.assertEqual(meter2.type, response_content[1]['type'])
        self.assertEqual(meter2.number, response_content[1]['number'])
        self.assertEqual(meter2.unit, response_content[1]['unit'])


class TestApartmentMeterByManager(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment meter is not allowed to be created by a manager.
        """
        url = reverse('apartment-meters', kwargs={'pk': self.apartment5.id})
        data = {
            'type': METER_TYPES[0][0],
            'number': '12345',
            'unit': UNITS[0][0],
            }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class TestApartmentMeterByManagerOfCooperative(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment meter is successfully created by the manager.
        """
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        data = {
            'type': METER_TYPES[0][0],
            'number': '12345',
            'unit': UNITS[0][0],
            }
        response = self.cpost(url, self.manager, data)

        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        ameters = ApartmentMeter.objects.filter(apartment=self.apartment1)
        self.assertTrue(ameters.exists())
        ameter = ameters[0]
        self.assertTrue(ameter.apartment.id, self.apartment1.id)
        meter = ameter.meter
        self.assertTrue(METER_TYPES[0][0], meter.type)
        self.assertTrue('12345', meter.number)
        self.assertTrue(UNITS[0][0], meter.unit)

    def test_retrieving_list(self):
        """
        The apartment meters are successfully retrieved.
        """
        meter1 = Meter(type=METER_TYPES[0][0], number='1234', unit=UNITS[0][0])
        meter1.save()
        meter2 = Meter(type=METER_TYPES[0][1], number='4567', unit=UNITS[0][1])
        meter2.save()
        apartment_meter1 = ApartmentMeter(
            apartment=self.apartment1, meter=meter1)
        apartment_meter1.save()
        apartment_meter2 = ApartmentMeter(
            apartment=self.apartment1, meter=meter2)
        apartment_meter2.save()

        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(meter1.type, response_content[0]['type'])
        self.assertEqual('Heating', meter1.get_type_display())
        self.assertEqual(meter1.number, response_content[0]['number'])
        self.assertEqual(meter1.unit, response_content[0]['unit'])
        self.assertEqual('Square meters', meter1.get_unit_display())
        self.assertEqual(meter2.type, response_content[1]['type'])
        self.assertEqual(meter2.number, response_content[1]['number'])
        self.assertEqual(meter2.unit, response_content[1]['unit'])


class TestApartmentMeterByInhabitant(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment meter is not allowed to be created by inhabitant.
        """
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        data = {
            'type': METER_TYPES[0][0],
            'number': '12345',
            'unit': UNITS[0][0],
            }
        response = self.cpost(url, self.inhabitant, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieving_list(self):
        """
        The apartment meters are not allowed to be retrieved by inhabitant.
        """        
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class TestApartmentMeterByUnauthenticated(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment meter is not allowed to be created by
        unauthenticated.
        """
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        data = {
            'type': METER_TYPES[0][0],
            'number': '12345',
            'unit': UNITS[0][0],
            }
        response = self.cpost(url, None, data)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieving_list(self):
        """
        The apartment meters are not allowed to be retrieved by
        inhabitant.
        """        
        url = reverse('apartment-meters', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, None, {})

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.urls import reverse
from rest_framework import status
import json

from osbb.models import Apartment, House, HousingCooperative
from test.osbb.testcase import BaseAPITestCase


class TestApartmentByAdmin(BaseAPITestCase):

    def test_creation(self):
        """
        The house is created by admin.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house1.id})
        data = {
            'number': 22,
            'floor': 2,
            'entrance': 1,
            'room_number': 4,
            'total_area': 88,
            'dwelling_space': 66,
            'heating_area': 88,
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['number'], response_content['number'])
        self.assertEqual(data['floor'], response_content['floor'])
        self.assertEqual(data['entrance'], response_content['entrance'])
        self.assertEqual(data['room_number'], response_content['room_number'])
        self.assertEqual(data['total_area'], response_content['total_area'])
        self.assertEqual(
            data['dwelling_space'], response_content['dwelling_space'])
        self.assertEqual(
            data['heating_area'], response_content['heating_area'])

    def test_deletion(self):
        """
        The apartment is successfully deleted by admin.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cdelete(url, self.admin)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Apartment.objects.filter(pk=self.apartment1.id).exists())

    def test_retrieving_list(self):
        """
        The apartments are successfully retrieved by admin.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.admin)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(3, len(response_content))
        self.assertEqual(self.apartment1.id, response_content[0]['id'])
        self.assertEqual(self.apartment1.number, response_content[0]['number'])
        self.assertEqual(self.apartment2.id, response_content[1]['id'])
        self.assertEqual(self.apartment2.number, response_content[1]['number'])
        self.assertEqual(self.apartment3.id, response_content[2]['id'])
        self.assertEqual(self.apartment3.number, response_content[2]['number'])

    def test_retrieving_item(self):
        """
        The apartment is successfully retrieved by admin.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.admin)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.apartment1.id, response_content['id'])
        self.assertEqual(self.apartment1.number, response_content['number'])


class TestApartmentByManager(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment is not allowed to be created by manager which
        doesn't manage the cooperative.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house3.id})
        data = {
            'number': 22,
            'floor': 2,
            'entrance': 1,
            'room_number': 4,
            'total_area': 88,
            'dwelling_space': 66,
            'heating_area': 88,
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating(self):
        """
        The apartment is not allowed to be updated by manager which
        doesn't manage the cooperative.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment5.id})
        data = {
            'number': 33,
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting(self):
        """
        The apartment is not allowed to be deleted by a manager.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment5.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item(self):
        """
        The apartment is not allowed to be retrived by a manager if that
        apartment doesn't belong to manager's cooperative.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment5.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestApartmentByManagerOfCooperative(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment is created by manager which belongs to apartment's
        cooperative.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house1.id})
        data = {
            'number': 23,
            'floor': 2,
            'entrance': 1,
            'room_number': 4,
            'total_area': 88,
            'dwelling_space': 66,
            'heating_area': 88,
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_updating(self):
        """
        The apartment is successfully updated by manager of the
        cooperative. The apartment belongs to the cooperative.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        data = {
            'number': 1144,
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Apartment.objects.filter(number=1144).exists())

    def test_deleting(self):
        """
        The apartment is successfully deleted by manager of the
        cooperative. The apartment belongs to the cooperative.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Apartment.objects.filter(pk=self.apartment1.id).exists())

    def test_retrieving_list(self):
        """
        The apartments are retrieved, but only those which belongs to the
        cooperative which the manager manages.
        """
        url = reverse('apartment-list')
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        results = response_content['results']
        self.assertEqual(4, len(results))
        self.assertEqual(self.apartment1.id, results[0]['id'])
        self.assertEqual(self.apartment2.id, results[1]['id'])
        self.assertEqual(self.apartment3.id, results[2]['id'])
        self.assertEqual(self.apartment4.id, results[3]['id'])

    def test_retrieving_item(self):
        """
        The apartment is successfully retrieved.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.apartment1.id, response_content['id'])
        self.assertEqual(self.apartment1.number, response_content['number'])


class TestApartmentByInhabitant(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment is not allowed to be created by inhabitant.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house1.id})
        response = self.cpost(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating(self):
        """
        The apartment is not allowed to be updated by inhabitant.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        data = {
            'number': 33,
        }
        response = self.cput(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting(self):
        """
        The apartment is not allowed to deleted by inhabitant.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cdelete(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list(self):
        """
        The apartments are not allowed to be retrieved by inhabitant.
        """
        url = reverse('apartment-list')
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item(self):
        """
        The apartment is not allowed to be retrieved by inhabitant.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestApartmentByUnauthenticated(BaseAPITestCase):

    def test_creation(self):
        """
        The apartment is not allowed to be created by unauthenticated.
        """
        url = reverse('house-apartments', kwargs={'pk': self.house1.id})
        response = self.cpost(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating(self):
        """
        The apartment is not allowed to be updated by unauthenticated.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        data = {
            'number': 33,
        }
        response = self.cput(url, None, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting(self):
        """
        The apartment is not allowed to deleted by unauthenticated.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cdelete(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_list(self):
        """
        The apartments are not allowed to be retrieved by unauthenticated.
        """
        url = reverse('apartment-list')
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_item(self):
        """
        The apartment is not allowed to be retrieved by unauthenticated.
        """
        url = reverse('apartment-detail', kwargs={'pk': self.apartment1.id})
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

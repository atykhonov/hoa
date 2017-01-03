# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.urls import reverse
from rest_framework import status
import json

from osbb.models import House, HousingCooperative
from test.osbb.testcase import BaseAPITestCase


class TestHouseByAdmin(BaseAPITestCase):

    def test_creation(self):
        """
        The house is created by admin.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieving_list(self):
        """
        All existing houses is retrieved by admin.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(name='house', cooperative=cooperative)
        house.save()

        url = reverse('house-list')
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        results = response_content['results']
        self.assertEqual(4, len(results))
        self.assertEqual(self.house1.id, results[0]['id'])
        self.assertEqual(self.house2.id, results[1]['id'])
        self.assertEqual(self.house3.id, results[2]['id'])
        self.assertEqual(house.id, results[3]['id'])

    def test_retrieving_item(self):
        """
        The house is retrieved by admin.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.id, response_content['id'])
        self.assertEqual(self.house1.name, response_content['name'])


class TestHouseByManager(BaseAPITestCase):

    def test_creation(self):
        """
        Creation of a cooperative is not allowed for a manager, if this
        manager is not a manager of the cooperative.
        """
        fixture = AutoFixture(HousingCooperative)
        cooperative = fixture.create(1)[0]
        url = reverse('cooperative-houses', kwargs={'pk': cooperative.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating(self):
        """
        Updating by manager is not allowed for a manager, if this manager
        is not a manager of the cooperative.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(name='house', cooperative=cooperative)
        house.save()
        url = reverse('house-detail', kwargs={'pk': house.id})
        data = {
            'name': 'test',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list(self):
        """
        Only those houses are retrieved by manager, which belongs to his
        cooperative.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(name='house', cooperative=cooperative)
        house.save()

        url = reverse('house-list')
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        results = response_content['results']
        self.assertEqual(2, len(results))
        self.assertEqual(self.house1.id, results[0]['id'])
        self.assertEqual(self.house2.id, results[1]['id'])

    def test_retrieving_item(self):
        """
        Retrieving the item is not allowed for a manager which doesn't
        manage the cooperative.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        url = reverse('house-detail', kwargs={'pk': house.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHouseByManagerOfCooperative(BaseAPITestCase):

    def test_creation(self):
        """
        The house is created by the manage of the cooperative.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_updating(self):
        """
        The house is updated by the manage of the cooperative.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        data = {
            'name': 'test',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deleting(self):
        """
        The house is successfully deleted by the manager of the
        cooperative.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(House.objects.filter(pk=self.house1.id).exists())

    def test_retrieving_item(self):
        """
        The house is retrieved by manager of the cooperative.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.id, response_content['id'])
        self.assertEqual(self.house1.name, response_content['name'])


class TestHouseByInhabitant(BaseAPITestCase):

    def test_creation(self):
        """
        Creation of a cooperative is not allowed for a inhabitant.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating(self):
        """
        The house is not allowed to be updated by inhabitant.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test',
        }
        response = self.cput(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list(self):
        """
        Retrieving list by inhabitant is not allowed.
        """
        url = reverse('house-list')
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item(self):
        """
        Retrieving the item is not allowed for an inhabitant.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHouseByUnauthenticated(BaseAPITestCase):

    def test_creation(self):
        """
        The house is forbidden to be created by an unauthenticated.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        response = self.cpost(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating(self):
        """
        The house is forbidden to be updated by an unauthenticated.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        response = self.cput(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_list(self):
        """
        Retrieving list by unauthenticated is not allowed.
        """
        url = reverse('house-list')
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_item(self):
        """
        Retrieving the item is not allowed for an unauthenticated.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
import json

from osbb.models import Service
from test.osbb.testcase import BaseAPITestCase


class ServiceByAdmin(BaseAPITestCase):

    def test_creation(self):
        """
        The service is created.
        """
        url = reverse('service-list')
        name = 'test-service'
        unit = 'uah/l'
        data = {
            'name': name,
            'unit': unit,
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(Service.objects.filter(name=name, unit=unit).exists())

    def test_updating(self):
        """
        The service is updated.
        """
        name = 'myservice'
        unit = 'myunit'
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        data = {
            'name': name,
            'unit': unit,
        }
        response = self.cput(url, self.admin, data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(
            Service.objects.filter(name=name, unit=unit).exists())

    def test_deletion(self):
        """
        The service is successfully deleted.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        response = self.cdelete(url, self.admin)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(Service.objects.filter(pk=self.service1.id).exists())

    def test_retrieving_list(self):
        """
        The services are successfully retrieved.
        """
        url = reverse('service-list')
        response = self.cget(url, self.admin, {})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response_content = json.loads(response.content.decode('utf-8'))
        results = response_content['results']
        self.assertEqual(self.service1.id, results[0]['id'])
        self.assertEqual(self.service2.id, results[1]['id'])

    def test_retrieving_item(self):
        """
        The service is successfully retrieved.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        response = self.cget(url, self.admin, {})

        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.service1.id, response_content['id'])
        self.assertEqual(self.service1.name, response_content['name'])


class ServiceByManager(BaseAPITestCase):

    def test_creation(self):
        """
        The service is not allowed to be created.
        """
        url = reverse('service-list')
        data = {
            'name': 'test-service',
            'unit': 'uah/l',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_updating(self):
        """
        The service is not allowed to be updated.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        data = {
            'name': 'myservice',
            'unit': 'myunit',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_deletion(self):
        """
        The service is successfully deleted.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        response = self.cdelete(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieving_list(self):
        """
        The services are successfully retrieved.
        """
        url = reverse('service-list')
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_retrieving_item(self):
        """
        The service is successfully retrieved.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class ServiceByUnauthenticated(BaseAPITestCase):

    def test_retrieving_list(self):
        """
        The services are not allowed to be retrieved.
        """
        url = reverse('service-list')
        response = self.cget(url, None, {})

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_retrieving_item(self):
        """
        The service is not allowed to be retrieved.
        """
        url = reverse('service-detail', kwargs={'pk': self.service1.id})
        response = self.cget(url, None, {})

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

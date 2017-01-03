# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.urls import reverse
from rest_framework import status
import json

from osbb.models import HousingCooperative, Service
from test.osbb.testcase import BaseAPITestCase


class TestCooperativeByAdmin(BaseAPITestCase):

    def test_creation(self):
        """
        The cooperative is created with specific name.
        """
        url = reverse('cooperative-list')
        itn = '1234567890'
        edrpou = '2345678901'
        certificate = '3456780912'
        legal_address = 'legal address'
        physical_address = 'physical address'
        phone_number = '0961122333'
        data = {
            'name': 'test',
            'individual_tax_number': itn,
            'edrpou': edrpou,
            'certificate': certificate,
            'legal_address': legal_address,
            'physical_address': physical_address,
            'phone_number': phone_number,
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        query = HousingCooperative.objects.filter(name='test')
        hc = query[0]
        self.assertTrue(query.exists())
        self.assertEqual(itn, hc.individual_tax_number)
        self.assertEqual(edrpou, hc.edrpou)
        self.assertEqual(certificate, hc.certificate)
        self.assertEqual(legal_address, hc.legal_address)
        self.assertEqual(physical_address, hc.physical_address)
        self.assertEqual(phone_number, hc.phone_number)

    def test_deleting(self):
        """
        The cooperative is successfully deleted by admin.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cdelete(url, self.admin)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            HousingCooperative.objects.filter(
                pk=self.cooperative1.id).exists())

    def test_retrieving_list(self):
        """
        The list of cooperatives is retrieved by admin.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_item(self):
        """
        The cooperative is retrieved by admin.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_houses(self):
        """
        Houses are retrieved by an admin.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.name, response_content[0]['name'])
        self.assertEqual(self.house1.address, response_content[0]['address'])
        self.assertEqual(self.house2.name, response_content[1]['name'])
        self.assertEqual(self.house2.address, response_content[1]['address'])

    def test_retrieving_services(self):
        """
        Services are retrieved by an admin.
        """
        url = reverse(
            'cooperative-services', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.hc_service1.id, response_content[0]['id'])
        self.assertEqual(
            self.hc_service1.service.id, response_content[0]['service'])
        self.assertEqual(
            self.hc_service1.cooperative.id,
            response_content[0]['cooperative']
            )
        self.assertEqual(self.hc_service1.notes, response_content[0]['notes'])

        self.assertEqual(self.hc_service2.id, response_content[1]['id'])
        self.assertEqual(
            self.hc_service2.service.id, response_content[1]['service'])
        self.assertEqual(
            self.hc_service2.cooperative.id,
            response_content[1]['cooperative']
        )
        self.assertEqual(self.hc_service2.notes, response_content[1]['notes'])

    def test_service_creation(self):
        """
        The service is created by an admin.
        """
        service_fixture = AutoFixture(Service)
        service = service_fixture.create(1)[0]
        url = reverse(
            'cooperative-services', kwargs={'pk': self.cooperative1.id})
        data = {
            'service': service.id,
            'notes': 'some notes',
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_service_creation_invalid_service(self):
        """
        The service is created by an admin.
        """
        url = reverse(
            'cooperative-services', kwargs={'pk': self.cooperative1.id})
        data = {
            'service': 442020,
            'notes': 'some notes',
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            response.data['service'][0],
            u'Invalid pk "442020" - object does not exist.'
        )


class TestCooperativeByManager(BaseAPITestCase):

    def test_creation(self):
        """
        Creation of a cooperative is not allowed for a manager.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting(self):
        """
        The cooperative is not allowed to be deleted by a manager.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cdelete(url, self.manager)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list(self):
        """
        The retrieving of cooperative list is forbidden for a manager.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            'You do not have permission to perform this action.',
            response.data['details']
        )

    def test_retrieving_item(self):
        """
        The cooperative is retrieved by manager.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_houses(self):
        """
        The houses are forbidden to be retrived by a manager which doesn't
        belong to the cooperative.
        """
        hc_fixture = AutoFixture(HousingCooperative)
        cooperative = hc_fixture.create(1)[0]

        url = reverse('cooperative-houses', kwargs={'pk': cooperative.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCooperativeByManagerOfCooperative(BaseAPITestCase):

    def test_updating(self):
        """
        The cooperative is updated by manager of the cooperative.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hc = HousingCooperative.objects.get(pk=self.cooperative1.id)
        self.assertEqual(self.cooperative1.id, hc.id)

    def test_deleting(self):
        """
        The cooperative is not allowed to be deleted by a manager.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cdelete(url, self.manager)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_houses(self):
        """
        The houses are retrieved by the manager of the cooperative.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCooperativeByInhabitant(BaseAPITestCase):

    def test_creation(self):
        """
        Creation of a cooperative is not allowed for a inhabitant.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating(self):
        """
        The cooperative is not allowed to be updated by inhabitant.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting(self):
        """
        The cooperative is not allowed to be deleted by a inhabitant.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cdelete(url, self.inhabitant)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list(self):
        """
        The retrieving of cooperative list is forbidden for a inhabitant.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item(self):
        """
        The cooperative is forbidden to be retrieved by an inhabitant.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_houses(self):
        """
        The houses are forbidden to be retrived by a inhabitant.
        """
        url = reverse(
            'cooperative-houses', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCooperativeByUnauthenticated(BaseAPITestCase):

    def test_creation(self):
        """
        Creation of a cooperative is not allowed for an unauthenticated.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, None, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating(self):
        """
        Updating is not allowed for a unauthenticated user.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, None, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting(self):
        """
        The cooperative is not allowed to be deleted by a
        unauthenticated user.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cdelete(url, None)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_list(self):
        """
        The unauthenticated is not allowed to retrieve the cooperative list.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_item(self):
        """
        The cooperative is forbidden to be retrieved by an
        unauthenticated.
        """
        url = reverse(
            'cooperative-detail', kwargs={'pk': self.cooperative1.id})
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

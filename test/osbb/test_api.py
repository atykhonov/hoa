# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import json

from osbb.models import House, HousingCooperative


User = get_user_model()


class BaseAPITestCase(APITestCase):

    def setUp(self):
        hc_fixture = AutoFixture(HousingCooperative)
        self.cooperative = hc_fixture.create(1)[0]

        house_fixture = AutoFixture(House)
        houses = house_fixture.create(2)
        self.house1 = houses[0]
        self.house2 = houses[1]

        self.inhabitant_email = 'inhabitant@example.com'
        self.inhabitant_password = 'ThkeT231'
        self.inhabitant = User(
            email=self.inhabitant_email,
            username=self.inhabitant_email,
            cooperative=self.cooperative,
        )
        self.inhabitant.set_password(self.inhabitant_password)
        self.inhabitant.passwd = self.inhabitant_password
        self.inhabitant.save()

        self.admin_email = 'administrator@example.com'
        self.admin_password = 'xnG3ZTix'
        self.admin = User(
            email=self.admin_email,
            username=self.admin_email,
            is_superuser=True,
        )
        self.admin.set_password(self.admin_password)
        self.admin.passwd = self.admin_password
        self.admin.save()

        self.manager_email = 'owner@example.com'
        self.manager_password = '20ThteEU'
        self.manager = User(
            email=self.manager_email,
            username=self.manager_email,
            cooperative=self.cooperative,
            is_staff=True,
        )
        self.manager.set_password(self.manager_password)
        self.manager.passwd = self.manager_password
        self.manager.save()

    def _cmethod(self, method, url, user, data=None):
        m = getattr(self.client, method)
        if user:
            token = self.getToken(user=user)
            return m(url, data, HTTP_AUTHORIZATION='JWT {}'.format(token))
        else:
            return m(url, data)

    def cget(self, url, user, data=None):
        return self._cmethod('get', url, user, data)

    def cput(self, url, user, data=None):
        return self._cmethod('put', url, user, data)

    def cpost(self, url, user, data=None):
        return self._cmethod('post', url, user, data)

    def cdelete(self, url, user, data=None):
        return self._cmethod('delete', url, user, data)

    def getToken(self, user=None):
        """
        Return token for the given `user`.
        """
        # data = {'email': 'manager@example.com', 'password': 'ThkeT231'}
        data = {'email': user.email, 'password': user.passwd}
        url = reverse('api-token-auth')
        response = self.client.post(url, data, format='json')
        response_content = json.loads(response.content.decode('utf-8'))
        return response_content["token"]


class TestHousingCooperative(BaseAPITestCase):

    def test_creation_by_manager(self):
        """
        Creation of a cooperative is not allowed for a manager.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creation_by_admin(self):
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

    def test_creation_by_inhabitant(self):
        """
        Creation of a cooperative is not allowed for a inhabitant.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creation_by_unauthenticated(self):
        """
        Creation of a cooperative is not allowed for an unauthenticated.
        """
        url = reverse('cooperative-list')
        data = {
            'name': 'test',
        }
        response = self.cpost(url, None, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating_by_manager(self):
        """
        The cooperative is updated by manager of the cooperative.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hc = HousingCooperative.objects.get(pk=self.cooperative.id)
        self.assertEqual(self.cooperative.id, hc.id)

    def test_updating_by_inhabitant(self):
        """
        The cooperative is not allowed to be updated by inhabitant.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating_by_unauthenticated(self):
        """
        Updating is not allowed for a unauthenticated user.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test-updated',
        }
        response = self.cput(url, None, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_by_admin(self):
        """
        The cooperative is successfully deleted by admin.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cdelete(url, self.admin)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            HousingCooperative.objects.filter(pk=self.cooperative.id).exists())

    def test_deleting_by_manager(self):
        """
        The cooperative is not allowed to be deleted by a manager.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cdelete(url, self.manager)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_by_inhabitant(self):
        """
        The cooperative is not allowed to be deleted by a inhabitant.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cdelete(url, self.inhabitant)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_by_unauthenticated(self):
        """
        The cooperative is not allowed to be deleted by a
        unauthenticated user.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cdelete(url, None)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_list_by_admin(self):
        """
        The list of cooperatives is retrieved by admin.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_list_by_manager(self):
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

    def test_retrieving_list_by_inhabitant(self):
        """
        The retrieving of cooperative list is forbidden for a inhabitant.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list_by_unauthenticated(self):
        """
        The unauthenticated is not allowed to retrieve the cooperative list.
        """
        url = reverse('cooperative-list')
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_item_by_admin(self):
        """
        The cooperative is retrieved by admin.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_item_by_manager(self):
        """
        The cooperative is retrieved by manager.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_item_by_inhabitant(self):
        """
        The cooperative is forbidden to be retrieved by an inhabitant.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item_by_unauthenticated(self):
        """
        The cooperative is forbidden to be retrieved by an
        unauthenticated.
        """
        url = reverse('cooperative-detail', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_houses_by_admin(self):
        """
        Houses are retrieved by an admin.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.name, response_content[0]['name'])
        self.assertEqual(self.house1.address, response_content[0]['address'])
        self.assertEqual(self.house2.name, response_content[1]['name'])
        self.assertEqual(self.house2.address, response_content[1]['address'])

    def test_retrieving_houses_by_manager(self):
        """
        The houses are forbidden to be retrived by a manager which doesn't
        belong to the cooperative.
        """
        hc_fixture = AutoFixture(HousingCooperative)
        cooperative = hc_fixture.create(1)[0]

        url = reverse('cooperative-houses', kwargs={'pk': cooperative.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_houses_by_manager_of_cooperative(self):
        """
        The houses are retrieved by the manager of the cooperative.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_houses_by_inhabitant(self):
        """
        The houses are forbidden to be retrived by a inhabitant.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHouse(BaseAPITestCase):

    def test_creation_by_admin(self):
        """
        The house is created by admin.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creation_by_manager(self):
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

    def test_creation_by_manager_of_cooperation(self):
        """
        The house is created by the manage of the cooperation.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creation_by_inhabitant(self):
        """
        Creation of a cooperative is not allowed for a inhabitant.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creation_by_unauthenticated(self):
        """
        The house is forbidden to be created by an unauthenticated.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        response = self.cpost(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updating_by_manager(self):
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

    def test_updating_by_manager_of_cooperation(self):
        """
        The house is updated by the manage of the cooperation.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        data = {
            'name': 'test',
        }
        response = self.cput(url, self.manager, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updating_by_inhabitant(self):
        """
        The house is not allowed to be updated by inhabitant.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        data = {
            'name': 'test',
        }
        response = self.cput(url, self.inhabitant, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating_by_unauthenticated(self):
        """
        The house is forbidden to be updated by an unauthenticated.
        """
        url = reverse('cooperative-houses', kwargs={'pk': self.cooperative.id})
        response = self.cput(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_list_by_admin(self):
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
        self.assertEqual(self.house1.id, results[0]['id'])
        self.assertEqual(self.house2.id, results[1]['id'])
        self.assertEqual(house.id, results[2]['id'])

    def test_retrieving_list_by_manager(self):
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

    def test_retrieving_list_by_inhabitant(self):
        """
        Retrieving list by inhabitant is not allowed.
        """
        url = reverse('house-list')
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_list_by_unauthenticated(self):
        """
        Retrieving list by unauthenticated is not allowed.
        """
        url = reverse('house-list')
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieving_item_by_admin(self):
        """
        The house is retrieved by admin.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.admin, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.id, response_content['id'])
        self.assertEqual(self.house1.name, response_content['name'])

    def test_retrieving_item_by_manager(self):
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

    def test_retrieving_item_by_manager_of_cooperative(self):
        """
        The house is retrieved by manager of the cooperative.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.manager, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(self.house1.id, response_content['id'])
        self.assertEqual(self.house1.name, response_content['name'])

    def test_retrieving_item_by_inhabitant(self):
        """
        Retrieving the item is not allowed for an inhabitant.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, self.inhabitant, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieving_item_by_unauthenticated(self):
        """
        Retrieving the item is not allowed for an unauthenticated.
        """
        url = reverse('house-detail', kwargs={'pk': self.house1.id})
        response = self.cget(url, None, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

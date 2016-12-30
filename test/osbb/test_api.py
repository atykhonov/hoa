# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)
import json

from osbb.models import HousingCooperative
from osbb.views.cooperative import HousingCooperativeViewSet


User = get_user_model()


class BaseAPITestCase(APITestCase):

    def setUp(self):
        fixture = AutoFixture(HousingCooperative)
        self.cooperative = fixture.create(1)[0]

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

    def cget(self, url, user, data=None):
        token = self.getToken(user=user)
        return self.client.get(
            url, data, HTTP_AUTHORIZATION='JWT {}'.format(token))

    def cput(self, url, user, data=None):
        token = self.getToken(user=user)
        return self.client.put(
            url, data, HTTP_AUTHORIZATION='JWT {}'.format(token))

    def cpost(self, url, user, data=None):
        token = self.getToken(user=user)
        return self.client.post(
            url, data, HTTP_AUTHORIZATION='JWT {}'.format(token))

    def cdelete(self, url, user, data=None):
        token = self.getToken(user=user)
        return self.client.delete(
            url, data, HTTP_AUTHORIZATION='JWT {}'.format(token))

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
        data = {
            'name': 'test',
        }
        response = self.cpost(url, self.admin, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            HousingCooperative.objects.filter(name='test').exists())

    def test_updating_by_manager(self):
        """
        The cooperative is updated by manager.
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

# -*- coding: utf-8 -*-

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestHousingCooperative(APITestCase):

    def test_retrieve(self):
        url = reverse('cooperative-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

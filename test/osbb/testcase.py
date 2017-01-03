# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
import json

from osbb.models import (
    Apartment,
    House,
    HousingCooperative,
    HousingCooperativeService,
    Service,
)


User = get_user_model()


class BaseAPITestCase(APITestCase):

    def setUp(self):
        hc_fixture = AutoFixture(HousingCooperative)
        cooperatives = hc_fixture.create(2)
        self.cooperative1 = cooperatives[0]
        self.cooperative2 = cooperatives[1]

        house_fixture = AutoFixture(
            House, field_values={'cooperative': self.cooperative1})
        houses = house_fixture.create(2)
        self.house1 = houses[0]
        self.house2 = houses[1]

        house_fixture = AutoFixture(
            House, field_values={'cooperative': self.cooperative2})
        houses = house_fixture.create(1)
        self.house3 = houses[0]

        apartment_fixture = AutoFixture(
            Apartment, field_values={'house': self.house1})
        apartments = apartment_fixture.create(3)
        self.apartment1 = apartments[0]
        self.apartment2 = apartments[1]
        self.apartment3 = apartments[2]

        apartment_fixture = AutoFixture(
            Apartment, field_values={'house': self.house2})
        apartments = apartment_fixture.create(1)
        self.apartment4 = apartments[0]

        apartment_fixture = AutoFixture(
            Apartment, field_values={'house': self.house3})
        apartments = apartment_fixture.create(1)
        self.apartment5 = apartments[0]

        self.inhabitant_email = 'inhabitant@example.com'
        self.inhabitant_password = 'ThkeT231'
        self.inhabitant = User(
            email=self.inhabitant_email,
            username=self.inhabitant_email,
            cooperative=self.cooperative1,
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
            cooperative=self.cooperative1,
            is_staff=True,
        )
        self.manager.set_password(self.manager_password)
        self.manager.passwd = self.manager_password
        self.manager.save()

        service_fixture = AutoFixture(Service)
        services = service_fixture.create(2)
        self.service1 = services[0]
        self.service2 = services[1]

        self.hc_service1 = HousingCooperativeService(
            cooperative=self.cooperative1,
            service=self.service1,
            notes='notes1',
            )
        self.hc_service1.save()
        self.hc_service2 = HousingCooperativeService(
            cooperative=self.cooperative1,
            service=self.service2,
            notes='notes2',
            )
        self.hc_service2.save()

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
        data = {'email': user.email, 'password': user.passwd}
        url = reverse('api-token-auth')
        response = self.client.post(url, data, format='json')
        response_content = json.loads(response.content.decode('utf-8'))
        return response_content["token"]

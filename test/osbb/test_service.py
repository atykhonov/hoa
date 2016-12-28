# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import Service


class ServiceTestCase(TestCase):

    def test_service_creation(self):
        """
        Service is created with certain name and unit.
        """
        name = 'test'
        unit = 'unit'
        service = Service(name=name, unit=unit)

        service.save()

        self.assertEqual(name, service.name)
        self.assertEqual(unit, service.unit)

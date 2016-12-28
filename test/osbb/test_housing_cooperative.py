# -*- coding: utf-8 -*-

from django.test import TestCase

from osbb.models import HousingCooperative, HousingCooperativeService, Service


class HousingCooperativeTestCase(TestCase):

    def test_cooperative_creation(self):
        """
        Housing cooperative is created with certain attributes.
        """
        name = 'test'
        individual_tax_number = '1234567890'
        edrpou = '1876543209'
        certificate = '4567890123'
        legal_address = 'test str. 22, 33'
        physical_address = 'physical str. 44, 55'
        phone_number = '+380961122333'
        cooperative = HousingCooperative(
            name=name,
            individual_tax_number=individual_tax_number,
            edrpou=edrpou,
            certificate=certificate,
            legal_address=legal_address,
            physical_address=physical_address,
            phone_number=phone_number,
        )

        cooperative.save()

        self.assertEqual(name, cooperative.name)
        self.assertEqual(
            individual_tax_number, cooperative.individual_tax_number)
        self.assertEqual(edrpou, cooperative.edrpou)
        self.assertEqual(certificate, cooperative.certificate)
        self.assertEqual(legal_address, cooperative.legal_address)
        self.assertEqual(physical_address, cooperative.physical_address)
        self.assertEqual(phone_number, cooperative.phone_number)

    def test_cooperative_with_house(self):
        """
        Housing cooperative is created with houses.
        """
        cooperative = HousingCooperative()
        cooperative.save()

        cooperative.house_set.create(name='first')
        cooperative.house_set.create(name='second')

        houses = cooperative.house_set.all()
        self.assertEqual('first', houses[1].name)
        self.assertEqual('second', houses[0].name)

    def test_cooperative_with_service(self):
        """
        House cooperative is created with a service.
        """
        notes = 'notes'
        housing_cooperative = HousingCooperative()
        housing_cooperative.save()
        service = Service(name='service')
        service.save()
        cooperative_service = HousingCooperativeService(
            housing_cooperative=housing_cooperative,
            service=service,
            notes=notes,
        )
        cooperative_service.save()

        self.assertEqual('service', cooperative_service.service.name)
        self.assertEqual(notes, cooperative_service.notes)

    def test_cooperative_with_services(self):
        """
        House cooperative is created with several services.
        """
        notes = 'notes'
        housing_cooperative = HousingCooperative()
        housing_cooperative.save()
        service1 = Service(name='service1')
        service1.save()
        cooperative_service1 = HousingCooperativeService(
            housing_cooperative=housing_cooperative,
            service=service1,
            notes=notes,
        )
        cooperative_service1.save()
        service2 = Service(name='service2')
        service2.save()
        cooperative_service2 = HousingCooperativeService(
            housing_cooperative=housing_cooperative,
            service=service2,
            notes=notes,
        )
        cooperative_service2.save()

        self.assertEqual('service1', cooperative_service1.service.name)
        self.assertEqual('service2', cooperative_service2.service.name)
        self.assertEqual(notes, cooperative_service1.notes)
        self.assertEqual(notes, cooperative_service2.notes)

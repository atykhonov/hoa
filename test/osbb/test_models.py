# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from autofixture import AutoFixture
from django.test import TestCase
from django.utils import timezone

from osbb.models import (
    Apartment,
    ApartmentMeter,
    ApartmentMeterIndicator,
    ApartmentTariff,
    BaseModelTest,
    House,
    HouseTariff,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    PersonalAccount,
    Service,
    User,
)


class TestBaseModelTestCase(TestCase):

    def test_creation(self):
        """
        Created date is set and equals to date of today.
        """
        now = timezone.now()
        model = BaseModelTest()

        model.save()

        self.assertEqual(now.date(), model.created_date.date())
        self.assertEqual(now.hour, model.created_date.hour)

    def test_modification(self):
        """
        `modified_date` is changed when model is changed.
        """
        model = BaseModelTest()
        model.modified_date = date(year=2016, month=12, day=20)
        model.save()

        model.name = 'test'
        model.save()

        self.assertEqual('test', model.name)
        now = timezone.now()
        self.assertEqual(now.date(), model.created_date.date())
        self.assertEqual(now.hour, model.created_date.hour)


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
        self.assertEqual('first', houses[0].name)
        self.assertEqual('second', houses[1].name)

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


class HouseTestCase(TestCase):

    def test_house_creation(self):
        """
        House is created with certain attributes.
        """
        name = 'house'
        address = 'wide str. 22, 33'
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative, name=name, address=address)

        house.save()

        self.assertEqual(cooperative.id, house.cooperative.id)
        self.assertEqual(name, house.name)
        self.assertEqual(address, house.address)

    def test_get_cooperative(self):
        """
        The cooperative is retrieved from the house.
        """
        hc_fixture = AutoFixture(HousingCooperative)
        hc = hc_fixture.create(1)[0]
        house_fixture = AutoFixture(House)
        house = house_fixture.create(1)[0]

        cooperative = house.get_cooperative()

        self.assertEqual(hc.id, cooperative.id)


class ApartmentTestCase(TestCase):

    def test_apartment_creation(self):
        """
        Apartment is created with certain attributes.
        """
        number = 22
        floor = 11
        entrance = 1
        room_number = 3
        total_area = 40
        dwelling_space = 30
        heating_area = 30
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(
            house=house,
            number=number,
            floor=floor,
            entrance=entrance,
            room_number=room_number,
            total_area=total_area,
            dwelling_space=dwelling_space,
            heating_area=heating_area,
        )

        apartment.save()

        self.assertEqual(house.id, apartment.house.id)
        self.assertEqual(number, apartment.number)
        self.assertEqual(floor, apartment.floor)
        self.assertEqual(entrance, apartment.entrance)
        self.assertEqual(room_number, apartment.room_number)
        self.assertEqual(total_area, apartment.total_area)
        self.assertEqual(dwelling_space, apartment.dwelling_space)
        self.assertEqual(heating_area, apartment.heating_area)

    def test_get_cooperative(self):
        """
        The cooperative is retrieved from the apartment.
        """
        hc_fixture = AutoFixture(HousingCooperative)
        hc = hc_fixture.create(1)[0]
        AutoFixture(House).create(1)
        apartment_fixture = AutoFixture(Apartment)
        apartment = apartment_fixture.create(1)[0]

        cooperative = apartment.get_cooperative()

        self.assertEqual(hc.id, cooperative.id)


class PersonalAccountTestCase(TestCase):

    def test_personal_account_creation(self):
        """
        Personal account is created with certain attributes.
        """
        uid = '000102030'
        prefix = '0001'
        receipt_text = 'text'
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=10)
        apartment.save()
        personal_account = PersonalAccount(
            apartment=apartment,
            uid=uid,
            prefix=prefix,
            receipt_text=receipt_text,
        )

        personal_account.save()

        self.assertEqual(apartment.id, personal_account.apartment.id)
        self.assertEqual(uid, personal_account.uid)
        self.assertEqual(prefix, personal_account.prefix)
        self.assertEqual(receipt_text, personal_account.receipt_text)


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


class ApartmentMeterTestCase(TestCase):

    def test_apartment_meter_creation(self):
        """
        Apartment meter is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=20)
        apartment.save()
        meter = Meter()
        meter.save()
        apartment_meter = ApartmentMeter(apartment=apartment, meter=meter)
        apartment_meter.save()

        self.assertEqual(apartment_meter.apartment.id, apartment.id)
        self.assertEqual(apartment_meter.meter.id, meter.id)


class ApartmentMeterIndicatorTestCase(TestCase):

    def test_creation(self):
        """
        Apartment meter indicator is created with certain attributes.
        """
        now = timezone.now()
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=20)
        apartment.save()
        meter = Meter()
        meter.save()
        apartment_meter = ApartmentMeter(apartment=apartment, meter=meter)
        apartment_meter.save()
        meter_indicator = ApartmentMeterIndicator(
            apartment_meter=apartment_meter, date=now, value=20)
        meter_indicator.save()

        self.assertEqual(
            apartment_meter.id, meter_indicator.apartment_meter.id)
        self.assertEqual(now, meter_indicator.date)
        self.assertEqual(20, meter_indicator.value)


class ApartmentTariffTestCase(TestCase):

    def test_creation(self):
        """
        Apartment tariff is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=10)
        apartment.save()
        service = Service()
        service.save()
        date = timezone.now()
        tariff = ApartmentTariff(
            apartment=apartment,
            deleted=False,
            date=date,
            service=service,
            value=20,
        )

        tariff.save()

        self.assertEqual(apartment.id, tariff.apartment.id)
        self.assertEqual(date, tariff.date)
        self.assertEqual(False, tariff.deleted)
        self.assertEqual(service.id, tariff.service.id)
        self.assertEqual(20, tariff.value)


class HouseTariffTestCase(TestCase):

    def test_creation(self):
        """
        House tariff is created with certain attributes.
        """
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        service = Service()
        service.save()
        date = timezone.now()
        tariff = HouseTariff(
            house=house,
            date=date,
            service=service,
            value=20,
        )

        tariff.save()

        self.assertEqual(house.id, tariff.house.id)
        self.assertEqual(date, tariff.date)
        self.assertEqual(service.id, tariff.service.id)
        self.assertEqual(20, tariff.value)


class UserTestCase(TestCase):

    def test_is_manager(self):
        """
        If a user is not superuser and he is staff than this user is a
        manager.
        """
        user = User(is_staff=True, is_superuser=False)

        self.assertTrue(user.is_manager())

    def test_superuser_is_not_manager(self):
        """
        If a user is superuser, he is not a manager even he is a staff.
        """
        user = User(is_staff=True, is_superuser=True)

        self.assertFalse(user.is_manager())

    def test_can_manage_superuser(self):
        """
        The user, which is superuser, can manage the cooperative.
        """
        user = User(is_superuser=True)
        fixture = AutoFixture(HousingCooperative)
        cooperative = fixture.create(1)[0]

        self.assertTrue(user.can_manage(cooperative))

    def test_can_manage_manager(self):
        """
        The user cannot manage the cooperative if he is not manager of the
        cooperative.
        """
        user = User(is_staff=True)
        fixture = AutoFixture(HousingCooperative)
        cooperative = fixture.create(1)[0]

        self.assertFalse(user.can_manage(cooperative))

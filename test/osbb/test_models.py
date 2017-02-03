# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from autofixture import AutoFixture
from django.test import TestCase
from django.utils import timezone

from address import models as addr_models
from core.models import BaseModelTest
from osbb.models import (
    Account,
    Apartment,
    ApartmentTariff,
    House,
    HouseTariff,
    HousingCooperative,
    HousingCooperativeService,
    Meter,
    MeterIndicator,
    Service,
    User,
)


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
            cooperative=housing_cooperative,
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
            cooperative=housing_cooperative,
            service=service1,
            notes=notes,
        )
        cooperative_service1.save()
        service2 = Service(name='service2')
        service2.save()
        cooperative_service2 = HousingCooperativeService(
            cooperative=housing_cooperative,
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
        city = addr_models.City.get_default_city()
        street = addr_models.Street(
            city=city,
            name='korotka',
            type=addr_models.Street.get_default_type()
            )
        street.save()
        house = addr_models.House(street=street, number=35)
        house.save()
        address = addr_models.Address(city=city, street=street, house=house)
        address.save()
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative, address=address)

        house.save()

        self.assertEqual(cooperative.id, house.cooperative.id)
        self.assertEqual(address, house.address)

    def test_get_cooperative(self):
        """
        The cooperative is retrieved from the house.
        """
        hc_fixture = AutoFixture(HousingCooperative)
        hc = hc_fixture.create(1)[0]
        house_fixture = AutoFixture(
            House, field_values={'cooperative': hc}, generate_fk=True)
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


class AccountTestCase(TestCase):

    def test_personal_account_creation(self):
        """
        Personal account is created with certain attributes.
        """
        user = User()
        user.save()
        uid = '000102030'
        cooperative = HousingCooperative()
        cooperative.save()
        house = House(cooperative=cooperative)
        house.save()
        apartment = Apartment(house=house, number=10)
        apartment.save()
        account = Account(
            apartment=apartment,
            uid=uid,
            owner=user,
        )

        account.save()

        self.assertEqual(apartment.id, account.apartment.id)
        self.assertEqual(uid, account.uid)

    def test_get_tariff_apartment(self):
        """
        The apartment tariff is retrieved if it is defined, even if house
        tariff is also defined.
        """
        apartment_fixture = AutoFixture(Apartment, generate_fk=True)
        apartment = apartment_fixture.create(1)[0]
        house = apartment.house
        house.tariff = 10000
        house.save()
        apartment.tariff = 20000
        apartment.save()
        account = Account(apartment=apartment)

        self.assertEqual(20000, account.get_tariff())

    def test_get_tariff_house(self):
        """
        The house tariff is retrieved.
        """
        apartment_fixture = AutoFixture(Apartment, generate_fk=True)
        apartment = apartment_fixture.create(1)[0]
        house = apartment.house
        house.tariff = 10000
        house.save()
        account = Account(apartment=apartment)

        self.assertEqual(10000, account.get_tariff())


class AccountPidTestCase(TestCase):

    def test_get_pid_without_indexes(self):
        """
        If a house and apartment are without index, then the personal
        account id is generated in form of the following string:
        001000100100010.
        """
        addr_city = addr_models.City(name='Львів')
        addr_city.save()
        addr_street = addr_models.Street(
            city=addr_city, name='Городоцька', type='Street')
        addr_street.save()
        addr_house = addr_models.House(street=addr_street, number=17)
        addr_house.save()
        addr_apartment = addr_models.Apartment(house=addr_house, number=33)
        addr_apartment.save()
        address = addr_models.Address(
            city=addr_city,
            street=addr_street,
            house=addr_house,
            apartment=addr_apartment
            )
        address.save()
        house_fixture = AutoFixture(House, generate_fk=True)
        house = house_fixture.create(1)[0]
        apartment = Apartment(house=house, address=address)
        user_fixture = AutoFixture(User, generate_fk=True)
        user = user_fixture.create(1)[0]
        account = Account(apartment=apartment, owner=user)

        pid = account.get_pid()

        self.assertEquals('001000101700330', pid)


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
            meter=apartment_meter, date=now, value=20)
        meter_indicator.save()

        self.assertEqual(
            apartment_meter.id, meter_indicator.meter.id)
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

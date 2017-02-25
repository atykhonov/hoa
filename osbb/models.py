# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from address.models import Address
from core.models import BaseModel
from osbb.period import Period


METER_TYPES = (
    ('HT', 'Heating'),
    ('EL', 'Electricity'),
    ('WT', 'Water and wastewater'),
    ('WH', 'Water heating'),
    ('GS', 'Gas'),
)

UNITS = (
    ('M2', 'Square meters'),
    ('MK', 'Square meters per kilocalorie'),
    ('KW', 'Kilowatt'),
    ('CM', 'Cubic meter'),
)


class HousingCooperative(BaseModel):
    name = models.CharField(max_length=255)
    individual_tax_number = models.CharField(max_length=10, blank=True)
    edrpou = models.CharField(max_length=10, blank=True)
    certificate = models.CharField(max_length=10, blank=True)
    legal_address = models.CharField(max_length=255, blank=True)
    physical_address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=13, blank=True)

    def manager(self):
        """
        Return the manager of the cooperative.
        """
        managers = self.user_set.all()
        if managers:
            return managers[0]
        else:
            return None

    def houses_count(self):
        """
        Return count of houses which belongs to the cooperative.
        """
        return self.houses.count()
    # manager = models.OneToOneField(User, null=True)  # joined with auth_user
    # accountant = models.OneToOneField()  # joined with auth_user
    # pasportyst = models.OneToOneField()  # joined with auth_user
    # bank_accounts = models.OneToOneField  # joined with bank_accounts
    # ...


class User(AbstractUser):

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    cooperative = models.ForeignKey(
        HousingCooperative, models.SET_NULL, blank=True, null=True)

    def is_manager(self):
        """
        If a user is superuser, then it is not treated as a manager. If a
        user is not superuser and is staff than this user is a
        manager.
        """
        return not self.is_superuser and self.is_staff

    def is_manager_of(self, cooperative):
        """
        Return True if the user is manager of the given `cooperative`.
        """
        if cooperative is None:
            return False
        if self.is_manager() and self.cooperative.id == cooperative.id:
            return True
        return False

    def can_manage(self, cooperative):
        """
        Return True if the user can manage the given cooperative.
        """
        if self.is_superuser:
            return True
        if cooperative is None or self.cooperative is None:
            return False
        if self.is_staff and self.cooperative.id == cooperative.id:
            return True

    def is_owner(self, apartment):
        """
        Return true if the user is owner of the given `apartment`.
        """
        return self.account == apartment.account


class Service(BaseModel):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=2, choices=UNITS)
    # Required services are called services which are automatically
    # created when cooperative is created.
    required = models.BooleanField(default=False)
    requires_meter = models.BooleanField(default=False)
    tariff = models.DecimalField(
        max_digits=10, decimal_places=2, default=None, null=True)


# class Tariff(BaseModel):
#     # current = models.BooleanField()
#     service = models.ForeignKey(Service)


class House(BaseModel):
    cooperative = models.ForeignKey(HousingCooperative, related_name='houses')
    address = models.OneToOneField(Address, related_name='house_address')
    tariff = models.DecimalField(
        max_digits=10, decimal_places=2, default=None, null=True)

    def get_cooperative(self):
        """
        Return the cooperative of the house.
        """
        return self.cooperative

    def delete(self, *args, **kwargs):
        self.address.delete()
        return super().delete(*args, **kwargs)


class Apartment(BaseModel):
    house = models.ForeignKey(House, related_name='apartments')
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, related_name='apartment_address')
    floor = models.IntegerField(null=True, default=None)
    entrance = models.IntegerField(null=True, default=None)
    room_number = models.IntegerField(null=True, default=None)
    total_area = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)
    dwelling_space = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)
    heating_area = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)
    tariff = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)

    def get_cooperative(self):
        """
        Return the cooperative of the apartment.
        """
        return self.house.cooperative

    def delete(self, *args, **kwargs):
        self.address.delete()
        return super().delete(*args, **kwargs)


class Account(BaseModel):
    apartment = models.OneToOneField(Apartment)
    owner = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, related_name='account')
    first_name = models.CharField(
        blank=True, max_length=30, verbose_name='first name')
    last_name = models.CharField(
        blank=True, max_length=30, verbose_name='last name')
    is_staff = models.BooleanField(default=False, verbose_name='staff status')

    def get_tariff(self):
        tariff = self.apartment.tariff
        if not tariff:
            return self.apartment.house.tariff
        return tariff

    def get_pid(self):
        """
        Return personal account id.
        """
        indexes = ['', 'а', 'б', 'в', 'г']
        address = self.apartment.address
        city = address.city
        house = address.house
        house_index = indexes.index(house.index)
        apartment = address.apartment
        apartment_index = indexes.index(apartment.index)
        return '{0:0>3}{1:0>4}{2:0>3}{3:0>1}{4:0>3}{5:0>1}'.format(
            address.city.id,
            address.street.id,
            house.number,
            house_index,
            apartment.number,
            apartment_index
            )

    def get_cooperative(self):
        """
        Return the cooperative to which the account belongs to.
        """
        return self.apartment.get_cooperative()

    def update_balance(self, amount, comment, service_charge=None):
        """
        Change the balance with the given `amount` of money and given
        `comment`.
        """
        remainder = 0
        balance = self.get_balance()
        if balance:
            remainder = balance
        return AccountBalance.objects.create(
            account=self,
            amount=amount,
            remainder=remainder+amount,
            comment=comment,
            service_charge=service_charge,
            )

    def override_balance(self, amount, comment):
        """
        Change the current balance and set to it given `amount` following
        the given `comment`.
        """
        remainder = 0
        balance = self.get_balance()
        if balance:
            remainder = balance
        return AccountBalance.objects.create(
            account=self,
            amount=amount-remainder,
            remainder=amount,
            comment=comment,
            )

    def get_balance(self):
        """
        Get balance for the given `period`.
        """
        objects = AccountBalance.objects.filter(account=self)
        if objects.exists():
            return objects[0].remainder
        return None


class ApartmentTariff(BaseModel):
    apartment = models.ForeignKey(Apartment)
    date = models.DateField()
    deleted = models.BooleanField()
    service = models.ForeignKey(Service)  # One-to-One
    value = models.FloatField()


class HouseTariff(BaseModel):
    date = models.DateField()
    house = models.ForeignKey(House)
    service = models.ForeignKey(Service)  # One-to-One
    value = models.FloatField()


class Meter(BaseModel):
    apartment = models.ForeignKey(Apartment, related_name='meters')
    service = models.ForeignKey(Service)
    number = models.CharField(max_length=10)
    entry_date = models.DateField(null=True)
    verification_date = models.DateField(null=True)

    def get_cooperative(self):
        """
        Return the cooperative of the apartment.
        """
        return self.apartment.house.cooperative

    def get_indicator(self, period):
        """
        Get indicator for the given period.
        """
        indicators = self.indicators.filter(period=period)
        if indicators:
            return indicators[0]
        return None

    def create_indicators(self):
        """
        Create indicators for the previous and the current mounths.
        """
        date = datetime.datetime.now().date()
        period = datetime.date(
            day=1, month=date.month, year=date.year)
        MeterIndicator.objects.create(meter=self, period=period)

        last_month_date = period - datetime.timedelta(days=1)
        period = last_month_date.replace(day=1)
        MeterIndicator.objects.create(meter=self, period=period)


class MeterIndicator(BaseModel):
    meter = models.ForeignKey(Meter, related_name='indicators')
    period = models.DateField()
    date = models.DateField(null=True)
    value = models.IntegerField(null=True)

    def get_cooperative(self):
        """
        Return the cooperative of the apartment.
        """
        return self.meter.apartment.house.cooperative


class HousingCooperativeService(BaseModel):
    cooperative = models.ForeignKey(
        HousingCooperative, related_name='services')
    service = models.ForeignKey(Service)
    # FIXME: Review max length 255, may be increase.
    notes = models.CharField(max_length=255)

    class Meta:
        unique_together = (('cooperative', 'service', ), )


class Charge(BaseModel):
    account = models.ForeignKey(Account, related_name='charges')
    period = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class ServiceCharge(BaseModel):
    charge = models.ForeignKey(Charge, related_name='services')
    service = models.ForeignKey(Service)
    tariff = models.DecimalField(
        max_digits=10, decimal_places=2, default=None, null=True)
    indicator_beginning = models.CharField(max_length=10)
    indicator_end = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2)


class AccountBalance(BaseModel):
    account = models.ForeignKey(Account, related_name='balances')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remainder = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.CharField(max_length=100)
    service_charge = models.ForeignKey(
        ServiceCharge,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='balances',
        )
    rollback = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def rollback_balance(self):
        amount = 0 - self.amount
        remainder = self.account.get_balance() + amount
        comment = 'Rollback balance #{}'.format(self.id)
        AccountBalance.objects.create(
            account=self.account,
            amount=amount,
            remainder=remainder,
            comment=comment,
            service_charge=self.service_charge,
            rollback=True,
            )
        self.rollback = True
        self.save()


class BankAccount(BaseModel):
    cooperative = models.ForeignKey(HousingCooperative)
    mfo = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

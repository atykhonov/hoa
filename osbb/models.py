# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


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


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModelTest(BaseModel):
    name = models.CharField(max_length=50)


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


class Service(BaseModel):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=2, choices=UNITS)
    # Required services are called services which are automatically
    # created when cooperative is created.
    required = models.BooleanField(default=False)
    requires_meter = models.BooleanField(default=False)


class Tariff(BaseModel):
    # current = models.BooleanField()
    service = models.ForeignKey(Service)


class House(BaseModel):
    cooperative = models.ForeignKey(HousingCooperative, related_name='houses')
    street = models.CharField(max_length=30, blank=True)
    number = models.IntegerField(default=None, null=True)
    tariff = models.IntegerField(default=None, null=True)
    apartments_count = models.IntegerField(null=True)

    class Meta:
        ordering = ['street', 'number', ]

    def get_cooperative(self):
        """
        Return the cooperative of the house.
        """
        return self.cooperative

    @property
    def address(self):
        """
        Return the address of the house.
        """
        if self.street and self.number:
            return '{}, {}'.format(self.street, self.number)
        return ''


class Apartment(BaseModel):
    house = models.ForeignKey(House, related_name='apartments')
    number = models.IntegerField()
    floor = models.IntegerField(null=True)
    entrance = models.IntegerField(null=True)
    room_number = models.IntegerField(null=True)
    total_area = models.FloatField(null=True)
    dwelling_space = models.FloatField(null=True)
    heating_area = models.FloatField(null=True)
    tariff = models.IntegerField(default=None, null=True)

    def get_cooperative(self):
        """
        Return the cooperative of the apartment.
        """
        return self.house.cooperative


class Account(BaseModel):
    uid = models.CharField(max_length=100)
    apartment = models.OneToOneField(Apartment)
    owner = models.OneToOneField(User, null=True)
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


class MeterIndicator(BaseModel):
    meter = models.ForeignKey(Meter, related_name='indicators')
    period = models.DateField()
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
    personal_account = models.ForeignKey(Account)
    date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    tariff = models.IntegerField()
    indicator_beginning = models.CharField(max_length=10)
    indicator_end = models.CharField(max_length=10)
    value = models.IntegerField()

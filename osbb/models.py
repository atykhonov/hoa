# -*- coding: utf-8 -*-

from django.db import models


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModelTest(BaseModel):
    name = models.CharField(max_length=50)


class Service(BaseModel):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=10)


class Tariff(BaseModel):
    # current = models.BooleanField()
    service = models.ForeignKey(Service)


class Meter(BaseModel):
    type = models.CharField(max_length=10)
    number = models.CharField(max_length=10)
    unit = models.CharField(max_length=10)
    entry_date = models.DateField(null=True)
    verification_date = models.DateField(null=True)


class HousingCooperative(BaseModel):
    name = models.CharField(max_length=255)
    individual_tax_number = models.CharField(max_length=10)
    edrpou = models.CharField(max_length=10)
    certificate = models.CharField(max_length=10)
    legal_address = models.CharField(max_length=255)
    physical_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=13)
    # manager = models.OneToOneField()  # joined with auth_user
    # accountant = models.OneToOneField()  # joined with auth_user
    # pasportyst = models.OneToOneField()  # joined with auth_user
    # bank_accounts = models.OneToOneField  # joined with bank_accounts
    # ...


class House(BaseModel):
    housing_cooperative = models.ForeignKey(HousingCooperative)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)


class Apartment(BaseModel):
    house = models.ForeignKey(House)
    number = models.IntegerField()
    floor = models.IntegerField(null=True)
    entrance = models.IntegerField(null=True)
    room_number = models.IntegerField(null=True)
    total_area = models.FloatField(null=True)
    dwelling_space = models.FloatField(null=True)
    heating_area = models.FloatField(null=True)
    # TODO: owner = models.ForeignKey()  # auth_user
    # TODO: family_members = 


class PersonalAccount(BaseModel):
    uid = models.CharField(max_length=100, primary_key=True)
    prefix = models.CharField(max_length=10)
    receipt_text = models.CharField(max_length=255)
    apartment = models.OneToOneField(
        Apartment,
        on_delete=models.CASCADE,
    )


# Experimental

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

###


class ApartmentMeter(BaseModel):
    apartment = models.ForeignKey(Apartment)
    meter = models.ForeignKey(Meter)


class ApartmentMeterIndicator(BaseModel):
    apartment_meter = models.ForeignKey(ApartmentMeter)
    date = models.DateField()
    value = models.IntegerField()


class HousingCooperativeService(BaseModel):
    housing_cooperative = models.ForeignKey(HousingCooperative)
    service = models.ForeignKey(Service)  # One-to-One
    # FIXME: Review max length 255, may be increase.
    notes = models.CharField(max_length=255)


class Charge(BaseModel):
    pass

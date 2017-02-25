# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from osbb.models import Account, Charge, Meter, MeterIndicator, ServiceCharge


def calccharges(apartment=None, house=None):
    """
    Calculate the charges for the current month. Calculate charges for
    all accounts of the given `apartment` or `house`. If neither
    `apartment` nor `house` is specified, then calculate the charges
    for all existing accounts.
    """
    if house:
        accounts = Account.objects.filter(apartment__house=house)
    elif apartment:
        accounts = Account.objects.filter(apartment=apartment)
    else:
        accounts = Account.objects.all()

    date = datetime.datetime.now().date()
    period = datetime.date(day=1, month=date.month, year=date.year)
    prev_date = period - datetime.timedelta(days=1)
    prev_period = datetime.date(
        day=1, month=prev_date.month, year=prev_date.year)
    created_charges = []
    for account in accounts:
        charges = account.charges.filter(period=period)
        for charge in charges:
            for service_charge in charge.services.all():
                balances = service_charge.balances.filter(rollback=False)
                for balance in balances:
                    balance.rollback_balance()
            charge.delete()
        apartment = account.apartment
        hc_services = apartment.house.cooperative.services
        charge = Charge(account=account, period=period)
        charge.save()
        created_charges.append(charge)
        total = Decimal(0)
        for hc_service in hc_services.all():
            service = hc_service.service
            if service.requires_meter:
                meters = apartment.meters.filter(service=service)
                for meter in meters:
                    indicator = meter.get_indicator(period)
                    indicator_value = 0
                    if indicator and indicator.value:
                        indicator_value = indicator.value
                    indicator = meter.get_indicator(period=prev_period)
                    prev_indicator_value = 0
                    if indicator and indicator.value:
                        prev_indicator_value = indicator.value
                    value = Decimal(0)
                    if (indicator_value > prev_indicator_value
                        and service.tariff):
                        # Avoid an negative value.
                        value = (
                            (indicator_value - prev_indicator_value)
                            * meter.service.tariff
                            )
                    service_charge = ServiceCharge(
                        charge=charge,
                        service=service,
                        tariff=service.tariff,
                        indicator_beginning=prev_indicator_value,
                        indicator_end=indicator_value,
                        value=value
                        )
                    service_charge.save()
                    if value:
                        account.update_balance(
                            0 - value, 'Charge', service_charge)
                    total += value
            else:
                tariff = account.get_tariff()
                value = 0
                if tariff and apartment.total_area:
                    value = tariff * apartment.total_area
                service_charge = ServiceCharge(
                    charge=charge,
                    service=service,
                    tariff=tariff,
                    value=value
                    )
                service_charge.save()
                if value:
                    account.update_balance(
                        0 - value, 'Charge', service_charge)
                total += value
        charge.total = total
        charge.save()

    return created_charges


def create_indicators(period):
    """
    Create empty meter indicators for the given `period`.
    """
    indicators = []
    for meter in Meter.objects.all():
        indicator = meter.indicators.filter(period=period)
        if not indicator:
            indicator = MeterIndicator(meter=meter, period=period)
            indicator.save()
            indicators.append(indicator)
    return indicators

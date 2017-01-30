# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.management.base import BaseCommand

from osbb.models import Account, Charge, Meter, MeterIndicator, ServiceCharge


class Command(BaseCommand):

    help = 'Calculate the charges for the current month.'

    def handle(self, *args, **options):
        count = 0
        accounts = Account.objects.all()
        date = datetime.datetime.now().date()
        period = datetime.date(day=1, month=date.month, year=date.year)
        prev_date = period - datetime.timedelta(days=1)
        prev_period = datetime.date(
            day=1, month=prev_date.month, year=prev_date.year)
        for account in accounts:
            charges = account.charges.filter(period=period)
            if not charges:
                apartment = account.apartment
                hc_services = apartment.house.cooperative.services
                charge = Charge(account=account, period=period)
                charge.save()
                count += 1
                total = 0
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
                                indicator_value = indicator.value
                            value = 0
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
                            total += value
                    else:
                        tariff = account.get_tariff()
                        value = 0
                        if tariff and apartment.heating_area:
                            value = tariff * apartment.total_area
                        service_charge = ServiceCharge(
                            charge=charge,
                            service=service,
                            tariff=tariff,
                            value=value
                            )
                        service_charge.save()
                        total += value
                charge.total = total
                charge.save()

        self.stdout.write(
            self.style.SUCCESS(
                '%d charges has been successfully created!' %
                (count, )))

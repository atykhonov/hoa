# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.management.base import BaseCommand

from osbb.models import Meter, MeterIndicator


class Command(BaseCommand):

    help = 'Creates meter indicators for apartments for the current month.'

    def handle(self, *args, **options):
        count = 0
        for meter in Meter.objects.all():
            date = datetime.datetime.now().date()
            period = datetime.date(day=1, month=date.month, year=date.year)
            indicator = meter.indicators.filter(period=period)
            if not indicator:
                indicator = MeterIndicator(meter=meter, period=period)
                indicator.save()
                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                '%d meter indicator(s) has been successfully created!' %
                (count, )))

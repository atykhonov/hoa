# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from osbb.utils import create_indicators


class Command(BaseCommand):

    help = 'Creates meter indicators for apartments for the current month.'

    def handle(self, *args, **options):

        date = datetime.datetime.now().date()
        period = datetime.date(day=1, month=date.month, year=date.year)

        indicators = create_indicators(period=period)

        self.stdout.write(
            self.style.SUCCESS(
                '%d meter indicator(s) has been successfully created!' %
                (len(indicators), )))

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from osbb.utils import calccharges


class Command(BaseCommand):

    help = 'Calculate the charges for the current month.'

    def handle(self, *args, **options):

        count = len(calccharges())

        self.stdout.write(
            self.style.SUCCESS(
                '%d charges has been successfully created!' % (count, )))

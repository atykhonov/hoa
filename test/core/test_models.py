# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.test import TestCase
from django.utils import timezone

from core.models import BaseModelTest


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

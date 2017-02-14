# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime


class Period():
    """
    Represents period of time. Actually, its value is the date of the
    first day of a month. For example, 01/01/2017 means that the
    period equals to 01/01/2017-31/01/2017.
    """
    def __init__(self):
        """
        Initiate the period using present `date`.
        """
        date = datetime.datetime.now().date()
        self.period = datetime.date(day=1, month=date.month, year=date.year)

    def present(self):
        """
        Return period for the present month.
        """
        return self.period

    def previous(self):
        """
        Return period for the previous month.
        """
        prev_date = self.period - datetime.timedelta(days=1)
        prev_period = datetime.date(
            day=1, month=prev_date.month, year=prev_date.year)
        return prev_period

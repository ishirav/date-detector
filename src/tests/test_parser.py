# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from date_detector import Parser

class ParserTest(TestCase):

    def _check(self, parser, text, dates):
        matches = parser.parse(text)
        self.assertEqual(set([m.date.isoformat() for m in matches]), set(dates))

    def test_ymd(self):
        for month_before_day in (True, False):
            p = Parser(month_before_day=month_before_day)
            self._check(p, '2017-07-01', ['2017-07-01'])
            self._check(p, '2017-12-01', ['2017-12-01'])

    def test_dmy(self):
        p = Parser(month_before_day=False)
        self._check(p, '1/7/2017', ['2017-07-01'])
        self._check(p, '01/07/2017', ['2017-07-01'])
        self._check(p, '21/7/2017', ['2017-07-21'])
        self._check(p, '7/21/2017', [])
        self._check(p, '01/02/03', ['2003-02-01', '2001-02-03'])

    def test_mdy(self):
        p = Parser(month_before_day=True)
        self._check(p, '1/7/2017', ['2017-01-07'])
        self._check(p, '01/07/2017', ['2017-01-07'])
        self._check(p, '21/7/2017', [])
        self._check(p, '7/21/2017', ['2017-07-21'])
        self._check(p, '01/02/03', ['2003-01-02', '2001-02-03'])

    def test_english(self):
        for month_before_day in (True, False):
            p = Parser(month_before_day=month_before_day)
            self._check(p, 'October 9, 2017', ['2017-10-09'])
            self._check(p, 'October 9th, 2017', ['2017-10-09'])
            self._check(p, '9 October, 2017', ['2017-10-09'])
            self._check(p, '2017 October 9', ['2017-10-09'])

    def test_hebrew(self):
        p = Parser(dictionaries=('en', 'he'))
        self._check(p, 'אוקטובר 9, 2017', ['2017-10-09'])
        self._check(p, '9 אוקטובר 2017', ['2017-10-09'])
        self._check(p, 'ה-9 לאוקטובר, 2017', ['2017-10-09'])
        self._check(p, 'ה-9 באוקטובר, 2017', ['2017-10-09'])
        self._check(p, '2017-אוק-09', ['2017-10-09'])
        self._check(p, '2017 אוקטובר 9', ['2017-10-09'])

    def test_invalid_dates(self):
        for month_before_day in (True, False):
            p = Parser(month_before_day=month_before_day)
            for d in ['29/2/2017', '2/29/2017', 'May 35, 1970', '20/30/40', 'June 1985']:
                self._check(p, d, [])

    def test_out_of_range(self):
        p = Parser()
        self._check(p, '2049-12-31', ['2049-12-31'])
        self._check(p, '2050-01-01', [])
        self._check(p, '1950-01-01', ['1950-01-01'])
        self._check(p, '1949-12-31', [])

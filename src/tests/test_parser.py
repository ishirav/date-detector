from unittest import TestCase

from date_detector import Parser

class ParserTest(TestCase):

    def _check(self, parser, text, dates):
        matches = parser.parse(text)
        self.assertEquals([m.date.isoformat() for m in matches], dates)

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
        self._check(p, '01/02/03', ['2002-03-01', '2001-02-03', '2003-02-01'])

    def test_mdy(self):
        p = Parser(month_before_day=True)
        self._check(p, '1/7/2017', ['2017-01-07'])
        self._check(p, '01/07/2017', ['2017-01-07'])
        self._check(p, '21/7/2017', ['2017-07-21'])
        self._check(p, '7/21/2017', ['2017-07-21'])
        self._check(p, '01/02/03', ['2003-01-02', '2002-01-03', '2001-02-03'])

    def test_english(self):
        for month_before_day in (True, False):
            p = Parser(month_before_day=month_before_day)
            self._check(p, 'October 9, 2017', ['2017-10-09'])
            self._check(p, 'October 9th, 2017', ['2017-10-09'])
            #### FIXME self._check(p, '9 October, 2017', ['2017-10-09'])
            self._check(p, '2017 October 9', ['2017-10-09'])

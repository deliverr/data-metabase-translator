"""
Unit test translation of SQL strings
"""
from unittest import TestCase
from translator import SqlTranslator


class SqlTranslatorTest(TestCase):

    def test_simple(self):
        sql = "select id, name, value from mytable"
        translator = SqlTranslator(sql)
        assert not translator.changed()
        assert translator.sql() == sql

    def test_date(self):
        translator = SqlTranslator("select DATE(mytimestamp) as mydate from mytable")
        assert translator.changed()
        assert translator.sql() == "SELECT TO_DATE(mytimestamp) AS mydate FROM mytable"

    def test_date_with_convert_timestamp(self):
        sql = "select DATE (convert_timezone ('utc','America/Los_Angeles',mytimestamp)) " \
              "as mydate from mytable"
        translator = SqlTranslator(sql)
        assert translator.changed()
        assert translator.sql() == "SELECT TO_DATE (convert_timezone ('America/Los_Angeles',mytimestamp)) " \
                                   "AS mydate FROM mytable"

    def test_interval(self):
        sql = "select mydate +INTERVAL '-30 day' from mytable"
        translator = SqlTranslator(sql)
        assert translator.changed()
        assert translator.sql() == "SELECT dateadd(day, -30, mydate) FROM mytable"

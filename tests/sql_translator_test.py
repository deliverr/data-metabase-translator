"""
Unit test translation of SQL strings
"""
from unittest import TestCase
from translator import SqlTranslator


class SqlTranslatorTest(TestCase):

    def test_simple(self):
        sql = "SELECT id, name, value FROM mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == sql

    def test_date(self):
        translator = SqlTranslator("select DATE(mytimestamp) as mydate from mytable")
        assert translator.sql() == "SELECT TO_DATE(mytimestamp) AS mydate FROM mytable"

    def test_date_with_convert_timestamp(self):
        sql = "select DATE (convert_timezone ('utc','America/Los_Angeles',mytimestamp)) " \
              "as mydate from mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT TO_DATE (convert_timezone ('America/Los_Angeles',mytimestamp)) " \
                                   "AS mydate FROM mytable"

    def test_interval_dateadd(self):
        sql = "select mydate +INTERVAL '-30 day' from mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT DATEADD(day, -30, mydate) FROM mytable"

    def test_interval_dateadd_in_where_clause(self):
        sql = "SELECT mytimestamp FROM mytable WHERE mytimestamp > CURRENT_DATE - interval '24 hours'"
        translator = SqlTranslator(sql)
        assert translator.sql() == \
               "SELECT mytimestamp FROM mytable WHERE mytimestamp > DATEADD(hours, -24, CURRENT_DATE)"

    def test_interval_standalone(self):
        sql = "SELECT mytimestamp FROM mytable WHERE mytimestamp - yourtimestamp >= interval '4 hour'"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT mytimestamp FROM mytable WHERE datediff(hour, mytimestamp, yourtimestamp) >= 4"

    def test_datediff(self):
        sql = "SELECT mytimestamp - your_timestamp as days from mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT datediff(day, mytimestamp, your_timestamp) AS days FROM mytable"


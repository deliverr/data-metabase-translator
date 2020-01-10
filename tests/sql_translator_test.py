"""
Unit test translation of SQL strings
"""
import pytest
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

    @pytest.mark.skip(reason="standalone interval conversion not yet implemented")
    def test_interval_standalone(self):
        sql = "SELECT mytimestamp FROM mytable WHERE mytimestamp - yourtimestamp >= interval '4 hour'"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT mytimestamp FROM mytable WHERE DATEDIFF(hour, mytimestamp, yourtimestamp) >= 4"

    @pytest.mark.skip(reason="interval to datediff conversion not yet implemented")
    def test_datediff(self):
        sql = "SELECT mytimestamp - your_timestamp as days from mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT DATEDIFF(day, mytimestamp, your_timestamp) AS days FROM mytable"

    def test_pound_as_identifier(self):
        sql = "SELECT #_of_codes from mytable LIMIT 1"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT num_of_codes FROM mytable LIMIT 1"

    def test_getdate(self):
        sql = "SELECT getdate() from mytable ORDER BY 1 DESC"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT current_timestamp() FROM mytable ORDER BY 1 DESC"

    def test_getdate_with_interval(self):
        sql = "SELECT mystuff FROM mytable WHERE mytable.createdate >= getdate() - interval '2 year'"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT mystuff FROM mytable WHERE mytable.createdate >= DATEADD(year, -2, current_timestamp())"
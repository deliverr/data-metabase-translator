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
        assert translator.sql() == "select TO_DATE(mytimestamp) as mydate from mytable"

    def test_date_with_convert_timestamp(self):
        sql = "select DATE (convert_timezone ('utc','America/Los_Angeles',mytimestamp)) " \
              "as mydate from mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "select TO_DATE (convert_timezone ('UTC','America/Los_Angeles',mytimestamp)) " \
                                   "as mydate from mytable"

    def test_pound_as_identifier(self):
        sql = "SELECT #_of_codes from mytable LIMIT 1"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT num_of_codes from mytable LIMIT 1"

    def test_getdate(self):
        sql = "SELECT getdate() from mytable ORDER BY 1 DESC"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT current_timestamp() from mytable ORDER BY 1 DESC"

    def test_getdate_with_interval(self):
        sql = "SELECT mystuff FROM mytable WHERE mytable.createdate >= getdate() - interval '2 year'"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT mystuff FROM mytable WHERE mytable.createdate >= current_timestamp() - interval '2 year'"

    def test_replace_underscores_with_json(self):
        sql = "SELECT my__redshift__json__workaround FROM mytable"
        translator = SqlTranslator(sql)
        assert translator.sql() == "SELECT my:redshift:json:workaround FROM mytable"


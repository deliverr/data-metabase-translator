from unittest import TestCase
from sql_translator import SqlTranslator


class SqlTranslatorTestCase(TestCase):

    def testSimple(self):
        sql = "select id, name, value from mytable"
        translator = SqlTranslator(sql)
        assert not translator.changed()
        assert translator.sql() == sql

    def testDate(self):
        translator = SqlTranslator("select DATE(mytimestamp) as mydate from mytable")
        assert translator.changed()
        assert translator.sql() == "select TO_DATE(mytimestamp) as mydate from mytable"

    def testDateWithConvertTimestamp(self):
        sql = "select DATE (convert_timezone ('utc','America/Los_Angeles',mytimestamp)) " \
              "as mydate from mytable"
        translator = SqlTranslator(sql)
        assert translator.changed()
        assert translator.sql() == "select TO_DATE (convert_timezone ('America/Los_Angeles',mytimestamp)) " \
                                   "as mydate from mytable"
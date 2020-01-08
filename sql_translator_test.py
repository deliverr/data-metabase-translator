from unittest import TestCase
from sql_translator import SqlTranslator


class SqlTranslatorTestCase(TestCase):

    def testSimple(self):
        sql = "select id, name, value from mytable"
        translator = SqlTranslator(sql)
        assert not translator.changed()
        assert translator.sql() == sql

    def testChange(self):
        translator = SqlTranslator("select DATE(mytimestamp) as mydate from mytable")
        assert translator.changed()
        assert translator.sql() == "select TO_DATE(mytimestamp) as mydate from mytable"
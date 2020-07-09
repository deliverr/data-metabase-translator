from unittest import TestCase

from metabase import QueryApi


class QueryApiTest(TestCase):

    def testExtractIdentifierTable(self):
        table = QueryApi.extract_identifier("Object 'DB.SCHEMA.TABLE' does not exist or not authorized.")
        assert table == 'DB.SCHEMA.TABLE'

    def testExtractIdentifierSchema(self):
        schema = QueryApi.extract_identifier("Schema 'DB.SCHEMA' does not exist or not authorized.")
        assert schema == 'DB.SCHEMA'

    def testExtractIdentifierColumn(self):
        column = QueryApi.extract_identifier("SQL compilation error: error line 6 at position 60\ninvalid identifier 'PROPERTIES__CSEMANAGER__VALUE'")
        assert column == 'PROPERTIES__CSEMANAGER__VALUE'

    def testExtractIdentifierRedshiftRelation(self):
        column = QueryApi.extract_identifier("[Amazon](500310) Invalid operation: relation \"myschema.myview\" does not exist")
        assert column == 'myschema.myview'

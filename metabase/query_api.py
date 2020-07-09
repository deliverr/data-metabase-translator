import re
import sys

from collections import namedtuple
from metabasepy import Client

from metabase import QueryReport

QueryAttempt = namedtuple('QueryAttempt', ('query_report', 'object_name', 'error', 'status'))


class QueryApi:

    def __init__(self, username, password):
        self.client = Client(base_url='http://localhost:3000',
                             username=username, password=password)
        self.client.authenticate()

    def attempt_query(self, query_report: QueryReport) -> QueryAttempt:
        try:
            query_resource = self.client.cards.query(query_report.card_id)
            error = query_resource['error'] if query_resource['status'] == 'failed' else None
            print(f"{query_report.card_id} {query_resource['status']} {error}")
            return QueryAttempt(query_report=query_report, object_name=QueryApi.extract_identifier(error),
                                status=query_resource['status'], error=error)
        except:
            err = sys.exc_info()[0]
            print(f"{query_report.card_id} {err}")
            return QueryAttempt(query_report=query_report, object_name=None, status='error', error=err)

    @staticmethod
    def extract_identifier(error: str):
        if error is None:
            return None
        for regex in ["(Object|Schema) '(?P<name>.+?)' does not exist",
                      "invalid identifier '(?P<name>.+?)'",
                      'relation "(?P<name>.+?)" does not exist',
                      'Unknown function (?P<name>.+?)',
                      "View definition for '(?P<name>.?)'"]:
            m = re.search(regex, error)
            if m:
                return m.group("name")
        m = re.search("(You'll need to pick a value|missing required parameters|Unable to substitute parameters)", error)
        if m:
            return "<requires parameters>"
        m = re.search("Timestamp '(.+?)' is not recognized", error)
        if m:
            return "<timestamp not recognized>"
        m = re.search("Numeric value '(.+?)' is not recognized", error)
        if m:
            return "<numeric value not recognized>"

        return None

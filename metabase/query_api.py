import sys

from collections import namedtuple
from metabasepy import Client

from metabase import QueryReport

QueryAttempt = namedtuple('QueryAttempt', ('queryReport', 'error', 'status'))


class QueryApi:

    def __init__(self, username, password):
        self.client = Client(base_url='http://deliverr-metabase-staging.us-east-1.elasticbeanstalk.com',
                             username=username, password=password)
        self.client.authenticate()

    def attempt_query(self, query_report: QueryReport) -> QueryAttempt:
        try:
            query_resource = self.client.cards.query(query_report.card_id)
            error = query_resource['error'] if query_resource['status'] == 'failed' else None
            print(f"{query_report.card_id} {query_resource['status']} {error}")
            return QueryAttempt(queryReport=query_report, status=query_resource['status'], error=error)
        except:
            err = sys.exc_info()[0]
            print(f"{query_report.card_id} {err}")
            return QueryAttempt(queryReport=query_report, status='error', error=err)

"""
Fetches query_execution data from Metabase postgresql database
"""
from collections import namedtuple
import psycopg2.extras
from typing import List

from metabase import Properties

QueryReport = namedtuple('QueryReport', ('runs', 'card_id', 'dashboard_id', 'pulse_id', 'native', 'context'))


class QueryExecutionRepo:

    def __init__(self, props: Properties):
        self.props = props
        self.conn = psycopg2.connect(**props.db._asdict())
        self.database_id = props.target.database_id

    def fetch_active(self, days_ago=90) -> List[QueryReport]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(f"select count(*) as runs, card_id, dashboard_id, pulse_id, native, context "
                       f"from query_execution "
                        f"where started_at > current_timestamp - interval '{days_ago} days' "
                        f"and error is null and context != 'ad-hoc' "
                       f"group by 2, 3, 4, 5, 6 order by 1 desc;")
        raw_query_reports = cursor.fetchall()

        query_reports = [
            QueryReport(r['runs'], r['card_id'], r['dashboard_id'], r['pulse_id'], r['native'], r['context'])
            for r in raw_query_reports]

        cursor.close()
        return query_reports

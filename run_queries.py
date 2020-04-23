"""
Reads active queries from Metabase, invokes REST API and reports errors
"""
from collections import namedtuple
from typing import List

from metabase import Properties, QueryApi, QueryAttempt, QueryExecutionRepo, QueryReport, ReportCardError, ReportCardRepo


def get_query_reports(props) -> List[QueryReport]:
    repo = QueryExecutionRepo(props)
    query_reports = repo.fetch_active(days_ago=30)
    print(f"Retrieved {len(query_reports)} queries")
    return query_reports


def attempt_queries(query_reports: List[QueryReport]) -> List[QueryAttempt]:
    query_api = QueryApi('myuser', 'mypassword')
    query_attempts = [query_api.attempt_query(q) for q in query_reports]

    return query_attempts


def filter_errors(query_attempts: List[QueryAttempt]) -> List[ReportCardError]:
    return [ReportCardError(q.query_report.card_id, q.query_report.dashboard_id,
                              q.query_report.pulse_id, q.object_name, q.error)
              for q in query_attempts if q.error is not None]


def main():
    query_exec_db_props = Properties(open('metabase.prod.yaml', 'r'))

    query_reports = get_query_reports(query_exec_db_props)
    query_attempts = attempt_queries(query_reports)
    errors = filter_errors(query_attempts)

    db_props = Properties(open('metabase.yaml', 'r'))
    ReportCardRepo(db_props).insert_errors(errors)

    print(f"Attempted {len(query_attempts)} queries, with {len(errors)} errors")


if __name__ == '__main__':
    main()

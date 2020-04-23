"""
Reads active queries from Metabase, invokes REST API and reports errors
"""
from typing import List

from metabase import Properties, QueryApi, QueryAttempt, QueryExecutionRepo, QueryReport, ReportCardError, ReportCardRepo


def get_query_reports(props) -> List[QueryReport]:
    repo = QueryExecutionRepo(props)
    query_reports = repo.fetch_active(days_ago=30)
    print(f"Retrieved {len(query_reports)} queries")
    return query_reports


def main():
    #query_exec_db_props = Properties(open('metabase.prod.yaml', 'r'))
    #query_reports = get_query_reports(query_exec_db_props)
    query_reports = []
    with open("error-card-ids.txt", "r") as f:
        for line in f:
            query_reports.append(QueryReport(1, int(line), None, None, True, None))

    db_props = Properties(open('metabase.yaml', 'r'))
    query_api = QueryApi('myuser', 'mypassword')
    error_count = 0
    for query_report in query_reports:
        query_attempt = query_api.attempt_query(query_report)
        if query_attempt.error is not None:
            error = ReportCardError(query_report.card_id, query_report.dashboard_id,
                                    query_report.pulse_id, query_attempt.object_name,
                                    query_attempt.error)
            ReportCardRepo(db_props).insert_error(error)
            error_count += 1

    print(f"Attempted {len(query_reports)} queries, with {error_count} errors")


if __name__ == '__main__':
    main()

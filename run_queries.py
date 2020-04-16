"""
Reads active queries from Metabase, invokes REST API and reports errors
"""
from collections import namedtuple

from metabase import Properties, QueryApi, QueryExecutionRepo

QueryAttempt = namedtuple('QueryAttempt', ('queryReport', 'error', 'httpStatus'))

def main():
    props = Properties(open('metabase.prod.yaml', 'r'))

    repo = QueryExecutionRepo(props)
    query_reports = repo.fetch_active()
    print(f"Retrieved {len(query_reports)} queries")

    query_api = QueryApi('myuser', 'mypassword')
    query_attempts = [query_api.attempt_query(q) for q in query_reports]

    print(f"Attempted {len(query_attempts)} queries")


if __name__ == '__main__':
    main()

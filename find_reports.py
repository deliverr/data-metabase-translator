"""
Reads queries from Metabase and finds reports that match a table name
"""
from metabase import Properties, ReportCardRepo
import sqlparse


def main():
    table = 'onboarding.seller'
    props = Properties(open('metabase.yaml', 'r'))

    repo = ReportCardRepo(props)
    report_cards = repo.fetchall()
    print(f"Retrieved {len(report_cards)} native queries")

    reports = []
    for report_card in report_cards:
        sql = report_card.dataset_query['native']['query']
        statements = sqlparse.parse(sql)
        for statement in statements:
            if references(statement, table):
              print(f"{report_card}")
              reports.append(report_card)

    print(f"Found {len(reports)}: {', '.join([id for r in reports])}")


def references(statement, table):
    if table in statement.value.lower():
        return True
    return False
    #if statement.is_group:
    #    for child in statement.tokens:
    #        return references(child, table)

if __name__ == '__main__':
    main()

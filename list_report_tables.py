"""
Lists Metabase report cards that use native queries, and the tables the queries reference
"""
import json
from metabase import Properties, ReportCardRepo
import sql_metadata


def main():
    props = Properties(open('metabase.yaml', 'r'))

    repo = ReportCardRepo(props)
    report_cards = repo.fetchall()
    print(f"Retrieved {len(report_cards)} native queries")

    reports = []
    for report_card in report_cards:
        sql = report_card.dataset_query['native']['query']
        report_tables = {
            "id": report_card.id,
            "name": report_card.name,
            "tables": sql_metadata.get_query_tables(sql)
        }
        reports.append(report_tables)

    with open(f'report-tables-{props.source.name}.json', 'w') as outfile:
        json.dump(reports, outfile)


if __name__ == '__main__':
    main()

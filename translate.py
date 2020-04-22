"""
Reads queries from Metabase, translates the SQL and stores the translations in report_card_migrations table.
"""
from metabase import Properties, ReportCardRepo
from translator import SqlTranslator


def main():
    props = Properties(open('metabase.yaml', 'r'))

    repo = ReportCardRepo(props)
    report_cards = repo.fetchall()
    print(f"Retrieved {len(report_cards)} native queries")

    report_card_migrations = []
    for report_card in report_cards:
        sql = report_card.dataset_query['native']['query']
        translator = SqlTranslator(sql)

        new_sql = translator.sql()
        if new_sql != sql:
            report_card_migrations.append(
                repo.create_migration(report_card, new_sql))

    repo.insert_migrations(report_card_migrations)

    print(f"Wrote {len(report_card_migrations)} rows to report_card_migration")


if __name__ == '__main__':
    main()

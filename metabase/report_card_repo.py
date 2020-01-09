"""
Fetches report card data from Metabase postgresql database and inserts report card migrations
"""
from collections import namedtuple
import json
import psycopg2.extras
from typing import List

from metabase import Properties

ReportCard = namedtuple('ReportCard', ('id', 'name', 'dataset_query', 'query_type', 'database_id'))
ReportCardMigration = namedtuple('ReportCardUpdate', ['id', 'original_query', 'query', 'dataset_query'])


class ReportCardRepo:

    def __init__(self, props: Properties):
        self.props = props
        self.conn = psycopg2.connect(**props.db._asdict())
        self.source_database_id = props.source.database_id
        self.target_database_id = props.target.database_id

    def fetchall(self) -> List[ReportCard]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(f"select id, name, dataset_query, query_type "
                       f"from report_card "
                       f"where database_id = {self.props.source.database_id}"
                       f"and query_type = 'native'")
        raw_report_cards = cursor.fetchall()

        report_cards = [
            ReportCard(card['id'],
                       card['name'],
                       json.loads(card['dataset_query']),
                       card['query_type'],
                       self.props.target.database_id)
            for card in raw_report_cards]

        cursor.close()
        return report_cards

    def create_migration(self, report_card: ReportCard, sql: str) -> ReportCardMigration:
        original_sql = report_card.dataset_query['native']['query']
        report_card.dataset_query['native']['query'] = sql
        report_card.dataset_query['database'] = self.target_database_id
        return ReportCardMigration(
            id=report_card.id,
            original_query=original_sql,
            query=sql,
            dataset_query=json.dumps(report_card.dataset_query))

    def insert_all(self, report_card_migrations: List[ReportCardMigration]):
        cursor = self.conn.cursor()
        for migration in report_card_migrations:
            insert = f"INSERT INTO report_card_migration " \
                     f"(card_id, source_database_id, target_database_id, original_query, query, dataset_query," \
                     f" created_at, updated_at) " \
                     f"VALUES (%s, %s, %s, %s, %s, %s, current_timestamp , current_timestamp )"
            cursor.execute(insert,
                           (migration.id,
                            self.source_database_id,
                            self.target_database_id,
                            migration.original_query,
                            migration.query,
                            migration.dataset_query))
        self.conn.commit()
        self.conn.close()

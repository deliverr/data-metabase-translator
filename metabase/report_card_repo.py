"""
Fetches report card data from Metabase postgresql database and inserts report card migrations
"""
from copy import deepcopy
from collections import namedtuple
import json
import psycopg2.extras
from typing import List

from metabase import Properties

ReportCard = namedtuple('ReportCard', ('id', 'name', 'dataset_query', 'query_type', 'database_id'))
ReportCardMigration = namedtuple('ReportCardMigration', ['id', 'source_dataset_query', 'target_dataset_query'])
ReportCardError = namedtuple('ReportCardError', ['card_id', 'dashboard_id', 'pulse_id', 'object_name', 'error'])


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

    def fetch_by_ids(self, ids: List[int]) -> List[ReportCard]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(f"select card_id as id, '' as name, source_dataset_query as dataset_query, 'native' as query_type "
                       f"from report_card_migration "
                       f"where source_database_id = {self.props.source.database_id} "
                       # f"and query_type = 'native' "
                       f"and card_id in ({','.join(list(map(str, ids)))})")
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
        source_dataset_query = report_card.dataset_query
        target_dataset_query = deepcopy(source_dataset_query)
        target_dataset_query['native']['query'] = sql
        target_dataset_query['database'] = self.target_database_id
        return ReportCardMigration(
            id=report_card.id,
            source_dataset_query=json.dumps(source_dataset_query),
            target_dataset_query=json.dumps(target_dataset_query))

    def insert_migrations(self, report_card_migrations: List[ReportCardMigration]):
        cursor = self.conn.cursor()
        for migration in report_card_migrations:
            insert = f"INSERT INTO report_card_migration " \
                     f"(card_id, source_database_id, target_database_id, source_dataset_query, target_dataset_query," \
                     f" created_at, updated_at) " \
                     f"VALUES (%s, %s, %s, %s, %s, current_timestamp , current_timestamp )"
            cursor.execute(insert,
                           (migration.id,
                            self.source_database_id,
                            self.target_database_id,
                            migration.source_dataset_query,
                            migration.target_dataset_query))
        self.conn.commit()
        self.conn.close()

    def insert_error(self, report_card_error: ReportCardError):
        self.insert_errors([report_card_error])

    def insert_errors(self, report_card_errors: List[ReportCardError]):
        cursor = self.conn.cursor()
        for error in report_card_errors:
            insert = f"INSERT INTO report_card_error " \
                     f"(card_id, dashboard_id, pulse_id, object_name, error, " \
                     f" created_at, updated_at) " \
                     f"VALUES (%s, %s, %s, %s, %s, current_timestamp , current_timestamp )"
            cursor.execute(insert,
                           (error.card_id,
                            error.dashboard_id,
                            error.pulse_id,
                            error.object_name,
                            str(error.error)[:512]))
        self.conn.commit()
        self.conn.close()

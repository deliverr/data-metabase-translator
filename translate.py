
from collections import namedtuple
import psycopg2.extras
import json
import yaml
from sql_translator import SqlTranslator

db_props = yaml.safe_load(open('metabase.yaml', 'r'))
conn = psycopg2.connect(**db_props['connection'])

cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
cursor.execute(f"select id, name, dataset_query, query_type "
               f"from report_card "
               f"where database_id = {db_props['source']['database_id']}"
               f"and query_type = 'native'")
report_cards = cursor.fetchall()
dataset_queries = [json.loads(card['dataset_query']) for card in report_cards if card['query_type'] == 'native']
print(f"Retrieved {len(report_cards)} native queries")

ReportCardUpdate = namedtuple('ReportCardUpdate', ['id', 'original_sql', 'sql'])
updates = []
for report_card in report_cards:
    dataset_query = json.loads(report_card['dataset_query'])
    sql = dataset_query['native']['query']
    translator = SqlTranslator(sql)
    if translator.changed():
        updates.append(
            ReportCardUpdate(
                id=report_card['id'],
                original_sql=sql,
                sql=translator.getSqlText())
        )

# todo: Either backup report_card table and update report_card or insert updates to new table



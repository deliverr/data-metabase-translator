
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
cursor.close()

dataset_queries = [json.loads(card['dataset_query']) for card in report_cards if card['query_type'] == 'native']
print(f"Retrieved {len(report_cards)} native queries")

ReportCardUpdate = namedtuple('ReportCardUpdate', ['id', 'original_query', 'query', 'dataset_query'])
source_id = db_props['source']['database_id']
target_id = db_props['target']['database_id']
updates = []
for report_card in report_cards:
    dataset_query = json.loads(report_card['dataset_query'])
    sql = dataset_query['native']['query']
    translator = SqlTranslator(sql)
    if translator.changed():
        dataset_query['native']['query'] = translator.sql()
        dataset_query['database'] = target_id
        updates.append(
            ReportCardUpdate(
                id=report_card['id'],
                original_query=sql,
                query=translator.sql(),
                dataset_query=json.dumps(dataset_query))
        )

# Insert updates to new table
cursor = conn.cursor()
for update in updates:
    insert = f"INSERT INTO report_card_migration " \
             f"(card_id, source_database_id, target_database_id, original_query, query, dataset_query," \
             f" created_at, updated_at) " \
             f"VALUES (%s, %s, %s, %s, %s, %s, current_timestamp , current_timestamp )"
    cursor.execute(insert, (update.id, source_id, target_id, update.original_query, update.query, update.dataset_query))
conn.commit()
conn.close()

print(f"Wrote {len(updates)} rows to report_card_migration")


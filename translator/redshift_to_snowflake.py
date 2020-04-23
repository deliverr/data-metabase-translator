"""
Matching and conversion rules for migrating Redshift SQL dialect to Snowflake
Reference: https://medium.com/@jthandy/how-compatible-are-redshift-and-snowflakes-sql-syntaxes-c2103a43ae84
"""
from typing import List
from translator.translate_token import TranslateToken


def redshift_to_snowflake(token: TranslateToken) -> None:
    try:

        if token.is_function():
            if token.matches('date'):
                token.set('TO_DATE')
            elif token.matches('getdate'):
                token.set('current_timestamp')
            elif token.matches('date_diff'):
                token.set('datediff')
            elif token.matches('datepart'):
                token.set('date_part')
        elif token.is_literal():
            if token.matches("'utc'"):
                token.set("'UTC'")
        elif token.matches('#'):
            token.set('num')
        elif token.is_identifier():
            if token.matches('"start-date"'):
                token.replace('"start-date"', "start_date")
            elif token.matches('warehousepoolinventorylog."delta"'):
                token.set('warehousepoolinventorylog.delta')
            elif token.matches('transit.fasttagdaysleft'):
                token.set('velocity.fasttagdaysleft')
            elif len(token.children) < 5 and token.contains('__'):
                token.replace('__', ':')

    except ValueError as e:
        print(token.get_statement())
        raise e

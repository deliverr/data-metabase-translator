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
            elif token.startswith('convert_timezone'):
                token.remove_sequential_children("'utc'", ',')
        elif token.is_literal():
            if token.matches("'utc'"):
                token.set("'UTC'")
        elif token.matches('#'):
            token.set('num')
        elif token.is_identifier():
            if len(token.children) < 5 and token.contains('__'):
                token.replace('__', ':')

    except ValueError as e:
        print(token.get_statement())
        raise e

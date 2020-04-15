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
            elif token.startswith('convert_timezone'):
                token.remove_sequential_children("'utc'", ',')
            elif token.matches('getdate'):
                token.set('current_timestamp')
        elif token.matches('#'):
            token.set('num')

    except ValueError as e:
        print(token.get_statement())
        raise e


def pop_beyond_whitespace(stack: List[TranslateToken]) -> TranslateToken:
    prev = stack.pop()
    while prev.is_whitespace():
        prev = stack.pop()
    return prev

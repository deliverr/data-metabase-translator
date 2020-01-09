"""
Matching and conversion rules for migrating Redshift SQL dialect to Snowflake
Reference: https://medium.com/@jthandy/how-compatible-are-redshift-and-snowflakes-sql-syntaxes-c2103a43ae84
"""
from translator.translate_token import TranslateToken


def redshift_to_snowflake(token: TranslateToken) -> None:
    if token.matches('interval'):
        # print(f"{self.get_statement()} uses 'interval'")
        pass

    if token.is_function():
        if token.matches('date'):
            token.set('TO_DATE')
        if token.startswith('convert_timezone'):
            token.remove_sequential_children("'utc'", ',')

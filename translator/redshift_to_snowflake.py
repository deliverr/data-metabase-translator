"""
Matching and conversion rules for migrating Redshift SQL dialect to Snowflake
Reference: https://medium.com/@jthandy/how-compatible-are-redshift-and-snowflakes-sql-syntaxes-c2103a43ae84
"""
from typing import List
from translator.translate_token import TranslateToken


def redshift_to_snowflake(token: TranslateToken) -> None:
    if token.matches('interval'):
        interval_to_dateadd(token)

    if token.is_function():
        if token.matches('date'):
            token.set('TO_DATE')
        if token.startswith('convert_timezone'):
            token.remove_sequential_children("'utc'", ',')


def interval_to_dateadd(token):
    date_var = None
    op = None
    new_children = []
    stack = []
    if token.parent and token.parent.children:
        for sibling in token.parent.children:
            if sibling == token:
                prev = pop_beyond_whitespace(stack)
                op = prev.value()
                if op not in ['+', '-']:
                    # todo: standalone interval
                    print(f"Migration of 'interval' in {token.get_statement()} not yet implemented")
                    return
                date_var = pop_beyond_whitespace(stack)
                new_children.extend(stack)
            elif not date_var:
                stack.append(sibling)
            elif sibling.is_whitespace() and not token.has_changed():
                pass
            elif sibling.is_literal():
                num, unit = sibling.value().replace("'", '').strip().split(' ')
                if num.startswith('-'):
                    if op == '+':
                        op = '-'
                    else:
                        op = '+'
                    num = num[1:]
                token.set(f"DATEADD({unit}, {op}{num}, {date_var.value()})")
                new_children.append(token)
            else:
                new_children.append(sibling)

        token.parent.children[:] = new_children
    else:
        print(f"ignoring 'interval' in {token.get_statement()}")


def pop_beyond_whitespace(stack: List[TranslateToken]) -> TranslateToken:
    prev = stack.pop()
    while prev.is_whitespace():
        prev = stack.pop()
    return prev
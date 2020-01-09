"""
Translates a SQL string from one dialect to another
"""

import sqlparse
from translator.translate_token import TranslateToken


class SqlTranslator:

    def __init__(self, sql):
        self._changed = False
        self._sql = self.translate(sql)

    def changed(self):
        return self._changed

    def translate(self, sql):
        statements = sqlparse.parse(sql)
        translate_tokens = [TranslateToken(parsed) for parsed in statements]
        for translate_token in translate_tokens:
            if translate_token.translate():
                self._changed = True

        if self._changed:
            values = [token.value() for token in translate_tokens]
            return ''.join(values)
        return sql

    def sql(self):
        return self._sql

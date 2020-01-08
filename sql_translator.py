import sqlparse
from translate_token import TranslateToken

class SqlTranslator:

    def __init__(self, sql):
        self._changed = False
        self._sql = self.translate(sql)

    def changed(self):
        return self._changed

    def translate(self, sql):
        statements = sqlparse.parse(sql)
        translate_tokens = []
        for parsed in statements:
            for token in parsed.tokens:
                translate_token = TranslateToken(token)
                translate_tokens.append(translate_token)
                if translate_token.translate():
                    self._changed = True

        if self._changed:
            values = [token.value() for token in translate_tokens]
            return ''.join(values)
        return sql

    def sql(self):
        return self._sql

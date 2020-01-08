from sqlparse import tokens

class TranslateToken:

    def __init__(self, token):
        self._token = token
        self._value = None
        self._children = []

    def translate(self):
        changed = False
        if self._token.is_group:
            for token in self._token.tokens:
                child = TranslateToken(token)
                self._children.append(child)
                if child.translate():
                    changed = True
        else:
            if self._token.ttype == tokens.Name:
                if self._token.value.lower() == 'date':
                    changed = True
                    self._value = 'TO_DATE'
            # else:
            #    self.print()

        return changed

    def value(self):
        if self._value is not None:
            return self._value
        if len(self._children) > 0:
            values = [child.value() for child in self._children]
            return ''.join(values)
        return self._token.value

    def print(self):
        if not self._token.is_whitespace:
            if self._token.is_group:
                for token in self._token.tokens:
                    token.print()
            else:
                print(f"{self._token} {self._token.ttype}")

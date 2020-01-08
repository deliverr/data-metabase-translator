from sqlparse.sql import Function, IdentifierList, Statement


class TranslateToken:

    def __init__(self, token):
        self._token = token
        self._value = None
        self._children = []

    def translate(self):
        changed = False
        if self._token.value.lower() == 'interval':
            # print(f"{self.get_statement(self._token)} uses 'interval'")
            pass

        if self.isfunction():
            if self._token.value.lower() == 'date':
                changed = True
                self._value = 'TO_DATE'
            if self._token.value.lower().startswith('convert_timezone'):
                changed = True
                self.remove_sequential_children("'utc'", ',')

        if self._token.is_group:
            for token in self._token.tokens:
                child = TranslateToken(token)
                self._children.append(child)
                if child.translate():
                    changed = True

        return changed

    def value(self):
        if self._value is not None:
            return self._value
        if len(self._children) > 0:
            values = [child.value() for child in self._children]
            return ''.join(values)
        return self._token.value

    def isfunction(self):
        return isinstance(self._token, Function) or isinstance(self._token.parent, Function)

    def isidentifier(self):
        return isinstance(self._token, IdentifierList) or isinstance(self._token.parent, IdentifierList)

    def has_parent_function(self, function_name):
        parent = self.get_parent(self._token)
        while parent is not None:
            if parent.isfunction() and parent.ischild_identifier(function_name):
                return True
            parent = self.get_parent(self._token)
        return False

    def get_parent(self, token):
        return TranslateToken(token.parent) if token.parent is not None else None

    def get_statement(self, token):
        if isinstance(token, Statement) or isinstance(self._token.parent, Statement):
            return token
        parent = self.get_parent(token)
        while parent is not None:
            statement = self.get_statement(parent._token)
            if statement is not None:
                return statement
            parent = self.get_parent(parent._token)
        raise ValueError(f"No statement found for token {token}!")

    def remove_sequential_children(self, *args):
        keep = []
        child_translators = []
        arg_index = 0
        for child in self._token.tokens:
            if arg_index < len(args) and child.value.lower() == args[arg_index]:
                arg_index += 1
            else:
                child_translators.append(TranslateToken(child))
                keep.append(child)

        if arg_index == 0:
            for child in child_translators:
                if child._token.is_group:
                    child.remove_sequential_children(*args)
        else:
            self._token.tokens[:] = keep

    def print(self):
        if not self._token.is_whitespace:
            if self._token.is_group:
                for token in self._token.tokens:
                    token.print()
            else:
                print(f"{self._token} {self._token.ttype}")

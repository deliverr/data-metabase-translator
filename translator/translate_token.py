"""
Wraps a sqlparse token with helper methods
"""

from sqlparse.sql import Function, IdentifierList, Statement, Token


class TranslateToken:

    def __init__(self, token, parent=None):
        self._token = token
        self._parent = parent
        self._value = None
        if token.is_group:
            self._children = [TranslateToken(child, self) for child in token.tokens]
        else:
            self._children = []

    def translate(self):
        changed = False
        if self._token.value.lower() == 'interval':
            # print(f"{self.get_statement()} uses 'interval'")
            pass

        if self.isfunction():
            if self._token.value.lower() == 'date':
                changed = True
                self._value = 'TO_DATE'
            if self._token.value.lower().startswith('convert_timezone'):
                changed = True
                self.remove_sequential_children("'utc'", ',')

        for child in self._children:
            if child.translate():
                changed = True

        return changed

    def value(self):
        if self._value is not None:
            return self._value
        if self._children:
            values = [child.value() for child in self._children]
            return ''.join(values)
        return self._token.normalized

    def isfunction(self):
        return isinstance(self._token, Function) or isinstance(self._token.parent, Function)

    def isidentifier(self):
        return isinstance(self._token, IdentifierList) or isinstance(self._token.parent, IdentifierList)

    def has_parent_function(self, function_name):
        parent = self.parent
        while parent is not None:
            if parent.isfunction() and parent.ischild_identifier(function_name):
                return True
            parent = parent.parent
        return False

    def get_statement(self):
        if isinstance(self._token, Statement) or isinstance(self._token.parent, Statement):
            return self._token
        parent = self.parent
        while parent is not None:
            statement = parent.get_statement()
            if statement is not None:
                return statement
            parent = parent.parent
        raise ValueError(f"No statement found for token {self._token}!")

    def remove_sequential_children(self, *values):
        """
        Remove children whose values match given strings.
        :param values: string values to match
        :return: None
        """
        keep = []
        arg_index = 0
        for child in self._children:
            if arg_index < len(values) and child._token.value.lower() == values[arg_index]:
                arg_index += 1
            else:
                keep.append(child)

        if arg_index == 0:
            for child in keep:
                if child._children:
                    child.remove_sequential_children(*values)
        else:
            self._token.tokens[:] = [child._token for child in keep]
            self._children[:] = keep

    def print(self):
        if not self._token.is_whitespace:
            if self._children:
                for child in self._children:
                    child.print()
            else:
                print(f"{self._token} {self._token.ttype}")

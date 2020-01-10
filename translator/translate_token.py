"""
Wraps a sqlparse token with helper methods
"""
from typing import Callable

from sqlparse import tokens
from sqlparse.sql import Function, Identifier, Statement, Token


class TranslateToken:

    def __init__(self, token: Token, parent=None):
        self._token = token
        self.parent = parent
        self._value = None
        if token.is_group:
            self.children = [TranslateToken(child, self) for child in token.tokens]
        else:
            self.children = []

    def translate(self, cb_sql_dialect_rules: Callable[['TranslateToken'], None]) -> str:
        """
        Translate a token (with all its children) using a given callback function

        :type cb_sql_dialect_rules: Callback function that applies SQL dialect migration rules
        """
        cb_sql_dialect_rules(self)

        for child in self.children:
            child.translate(cb_sql_dialect_rules)

        return self.value()

    def value(self):
        if self._value is not None:
            return self._value
        if self.children:
            values = [child.value() for child in self.children]
            return ''.join(values)
        return self._token.normalized

    def set(self, str):
        self._value = str

    def matches(self, value: str) -> bool:
        return self._token.value.lower() == value.lower()

    def startswith(self, value: str) -> bool:
        return self._token.value.lower().startswith(value.lower())

    def is_function(self):
        return isinstance(self._token, Function) or isinstance(self._token.parent, Function)

    def is_identifier(self):
        return isinstance(self._token, Identifier) or isinstance(self._token.parent, Identifier)

    def is_literal(self):
        return self._token.ttype in [tokens.Literal,
                                     tokens.Literal.String,
                                     tokens.Literal.Number,
                                     tokens.Literal.String.Single,
                                     tokens.Literal.Number.Single]

    def is_whitespace(self):
        return self._token.is_whitespace

    def has_changed(self):
        return self._value is not None

    def matches_ancestor_function(self, function_name):
        """
        Checks whether there is an ancestor token that matches a given function name

        :param function_name: str function name to match
        :return: bool
        """
        parent = self.parent
        while parent is not None:
            if parent.is_function() and parent.ischild_identifier(function_name):
                return True
            parent = parent._parent
        return False

    def get_statement(self):
        if isinstance(self._token, Statement) or isinstance(self._token.parent, Statement):
            return self._token
        parent = self.parent
        while parent is not None:
            statement = parent.get_statement()
            if statement is not None:
                return statement
            parent = parent._parent
        raise ValueError(f"No statement found for token {self._token}!")

    def remove_sequential_children(self, *values):
        """
        Remove children whose values match given strings.
        :param values: string values to match
        :return: None
        """
        keep = []
        arg_index = 0
        for child in self.children:
            if arg_index < len(values) and child._token.value.lower() == values[arg_index]:
                arg_index += 1
            else:
                keep.append(child)

        if arg_index == 0:
            for child in keep:
                if child.children:
                    child.remove_sequential_children(*values)
        else:
            self._token.tokens[:] = [child._token for child in keep]
            self.children[:] = keep

    def print(self):
        if not self._token.is_whitespace:
            if self.children:
                for child in self.children:
                    child.print()
            else:
                print(f"{self._token} {self._token.ttype}")

"""
Reads Metabase properties
"""
from collections import namedtuple

import yaml

DbProps = namedtuple('DbProps', ['host', 'port', 'user', 'password', 'dbname'])
DatabaseId = namedtuple('DatabaseId', ['name', 'database_id'])


class Properties:

    def __init__(self, file):
        props = yaml.safe_load(file)
        self.db = DbProps(**props['connection'])
        self.source = DatabaseId(**props['source'])
        self.target = DatabaseId(**props['target'])

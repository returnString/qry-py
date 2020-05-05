import sqlite3

from qry.common import export

from .sql import Connection

@export
def connect_sqlite(connstring: str) -> Connection:
	return Connection(sqlite3.connect(connstring, isolation_level = None))

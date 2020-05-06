from typing import Any, Optional

import sqlite3

from qry.common import export

from .sql import Connection, DBType

def sqlite_typecode(typecode: Any) -> Optional[DBType]:
	# FIXME: sqlite needs types too :(
	return DBType.STRING

@export
def connect_sqlite(connstring: str) -> Connection:
	return Connection(sqlite3.connect(connstring, isolation_level = None), sqlite_typecode)

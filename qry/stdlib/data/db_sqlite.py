from typing import Dict

import sqlite3

from qry.common import export
from qry.lang import String, Int, Float, Bool

from .sql import Connection
from .sql_codegen import ColumnMetadata

_affinity_map = {
	'text': String,
	'integer': Int,
}

def _sqlite_metadata(conn: Connection, table: str) -> Dict[str, ColumnMetadata]:
	cursor = conn.c.cursor()
	# FIXME: injection
	cursor.execute(f'select * from {table} limit 0')
	names = [desc[0] for desc in cursor.description]

	typeof_exprs = ', '.join([f'typeof({n})' for n in names])
	cursor.execute(f'select {typeof_exprs} from {table} limit 1')

	rows = cursor.fetchall()
	assert len(rows) == 1

	ret = {}
	for index, col_affinity in enumerate(rows[0]):
		ret[names[index]] = ColumnMetadata(_affinity_map[col_affinity])

	return ret

@export
def connect_sqlite(connstring: str) -> Connection:
	return Connection(sqlite3.connect(connstring, isolation_level = None), _sqlite_metadata)

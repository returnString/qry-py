from typing import Any, Optional

import psycopg2

from qry.common import export

from .sql import Connection, DBType

_oid_map = {
	# ints
	20: DBType.INT, # int8
	21: DBType.INT, # int2
	23: DBType.INT, # int4

	# strings
	25: DBType.STRING, # text
	1042: DBType.STRING, # char
	1043: DBType.STRING, # varchar
}

def postgres_typecode(typecode: Any) -> Optional[DBType]:
	return _oid_map.get(typecode)

@export
def connect_postgres(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(psycopg2.connect(
		host = host,
		port = port,
		dbname = database,
		user = user,
		password = password,
	), postgres_typecode)

	conn.c.autocommit = True # type: ignore
	return conn

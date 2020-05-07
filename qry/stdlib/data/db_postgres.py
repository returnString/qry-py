import psycopg2

from qry.common import export

from .sql import Connection, DBType, metadata_from_typecode_lookup

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

@export
def connect_postgres(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(psycopg2.connect(
		host = host,
		port = port,
		dbname = database,
		user = user,
		password = password,
	), metadata_from_typecode_lookup(_oid_map))

	conn.c.autocommit = True # type: ignore
	return conn

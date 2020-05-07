import psycopg2

from qry.common import export
from qry.lang import String, Int, Float, Bool

from .sql import Connection, metadata_from_typecode_lookup

_oid_map = {
	# ints
	20: Int, # int8
	21: Int, # int2
	23: Int, # int4

	# strings
	25: String, # text
	1042: String, # char
	1043: String, # varchar
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

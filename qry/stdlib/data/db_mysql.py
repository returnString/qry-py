import MySQLdb
from MySQLdb import FIELD_TYPE

from qry.common import export
from qry.lang import String, Int, Float, Bool

from .sql import Connection, metadata_from_typecode_lookup

_typecode_map = {
	FIELD_TYPE.VAR_STRING: String,
	FIELD_TYPE.VARCHAR: String,
	FIELD_TYPE.STRING: String,
	FIELD_TYPE.SHORT: Int,
	FIELD_TYPE.LONG: Int,
}

@export
def connect_mysql(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(MySQLdb.connect(
		host = host,
		port = port,
		db = database,
		user = user,
		passwd = password,
	), metadata_from_typecode_lookup(_typecode_map))

	conn.c.autocommit(True) # type: ignore
	return conn

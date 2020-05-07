import MySQLdb
from MySQLdb import FIELD_TYPE

from qry.common import export
from qry.lang import String, Int, Float, Bool, BinaryOp

from .sql_connection import Connection, ColumnMetadata, BinopRewrite
from .sql import metadata_from_typecode_lookup

_typecode_map = {
	FIELD_TYPE.VAR_STRING: String,
	FIELD_TYPE.VARCHAR: String,
	FIELD_TYPE.STRING: String,
	FIELD_TYPE.SHORT: Int,
	FIELD_TYPE.LONG: Int,
}

def _mysql_binop_rewrite(
	op: BinaryOp,
	lhs_meta: ColumnMetadata,
	lhs: str,
	rhs_meta: ColumnMetadata,
	rhs: str,
) -> BinopRewrite:
	if op == BinaryOp.ADD and lhs_meta.type == String and rhs_meta.type == String:
		return (ColumnMetadata(String), f'concat({lhs}, {rhs})')

	return None

@export
def connect_mysql(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(MySQLdb.connect(
		host = host,
		port = port,
		db = database,
		user = user,
		passwd = password,
	), metadata_from_typecode_lookup(_typecode_map), _mysql_binop_rewrite)

	conn.c.autocommit(True) # type: ignore
	return conn

from typing import Any, Optional

import MySQLdb
from MySQLdb import FIELD_TYPE

from qry.common import export

from .sql import Connection, DBType

_typecode_map = {
	FIELD_TYPE.VAR_STRING: DBType.STRING,
	FIELD_TYPE.VARCHAR: DBType.STRING,
	FIELD_TYPE.STRING: DBType.STRING,
	FIELD_TYPE.SHORT: DBType.INT,
	FIELD_TYPE.LONG: DBType.INT,
}

def mysql_typecode(typecode: Any) -> Optional[DBType]:
	return _typecode_map.get(typecode)

@export
def connect_mysql(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(MySQLdb.connect(
		host = host,
		port = port,
		db = database,
		user = user,
		passwd = password,
	), mysql_typecode)

	conn.c.autocommit(True) # type: ignore
	return conn

import MySQLdb

from qry.common import export

from .sql import Connection

@export
def connect_mysql(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(MySQLdb.connect(
		host = host,
		port = port,
		db = database,
		user = user,
		passwd = password,
	))

	conn.c.autocommit(True) # type: ignore
	return conn

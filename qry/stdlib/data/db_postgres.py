import psycopg2

from qry.stdlib.export import export

from .sql import Connection

@export
def connect_postgres(host: str, port: int, database: str, user: str, password: str) -> Connection:
	conn = Connection(psycopg2.connect(
		host = host,
		port = port,
		dbname = database,
		user = user,
		password = password,
	))

	conn.c.autocommit = True # type: ignore
	return conn

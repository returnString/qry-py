from typing import Optional, Iterable, Any
from typing_extensions import Protocol

import sqlite3

from .meta import AST

class DBCursor(Protocol):
	def execute(self, sql: str, parameters: Iterable[Any] = ...) -> 'DBCursor':
		...

class DBConn(Protocol):
	def cursor(self, cursorClass: Optional[type] = ...) -> DBCursor:
		...

class DataLib:
	def connect_sqlite(self, connstring: str) -> DBConn:
		return sqlite3.connect(connstring)

	def execute(self, conn: DBConn, sql: str) -> None:
		cursor = conn.cursor()
		cursor.execute(sql)

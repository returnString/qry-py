from typing import Optional, Iterable, Any, List
from typing_extensions import Protocol
from dataclasses import dataclass

import sqlite3

from .core import Number
from .meta import MetaLib

class DBCursor(Protocol):
	def execute(self, sql: str, parameters: Iterable[Any] = ...) -> 'DBCursor':
		...

	def fetchall(self) -> Any:
		...

class DBConn(Protocol):
	def cursor(self, cursorClass: Optional[type] = ...) -> DBCursor:
		...

class QueryStep(Protocol):
	def render(self, prev: str) -> str:
		...

@dataclass
class Filter:
	exprs: List[str]

	def render(self, source: str) -> str:
		cond = ' and '.join(self.exprs)
		return f'select * from ({source}) where {cond}'

@dataclass
class Count:
	def render(self, source: str) -> str:
		return f'select count(*) from ({source})s'

@dataclass
class QueryPipeline:
	conn: DBCursor
	source_table: str
	steps: List[QueryStep]

	def chain(self, step: QueryStep) -> 'QueryPipeline':
		steps = self.steps.copy()
		steps.append(step)
		return QueryPipeline(self.conn, self.source_table, steps)

	def execute(self) -> Any:
		query = f'select * from {self.source_table}'
		for step in self.steps:
			query = step.render(query)

		self.conn.execute(query)
		return self.conn.fetchall()

class DataLib:
	def connect_sqlite(self, connstring: str) -> DBConn:
		return sqlite3.connect(connstring)

	def execute(self, conn: DBConn, sql: str) -> None:
		cursor = conn.cursor()
		cursor.execute(sql)

	def get_table(self, conn: DBConn, table: str) -> QueryPipeline:
		return QueryPipeline(conn.cursor(), table, [])

	def filter(self, query: QueryPipeline, expr: MetaLib.Syntax) -> QueryPipeline:
		return query.chain(Filter([expr.render()]))

	def collect(self, query: QueryPipeline) -> Any:
		return query.execute()

	def count_rows(self, query: QueryPipeline) -> Number:
		query = query.chain(Count())
		data = query.execute()
		assert isinstance(data[0][0], int)
		return Number(data[0][0])

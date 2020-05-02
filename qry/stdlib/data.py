from typing import Optional, Iterable, Any, List, Dict
from typing_extensions import Protocol
from dataclasses import dataclass
from enum import Enum

import sqlite3

from ..syntax import Expr

from .core import Number
from .export import export

class DBCursor(Protocol):
	def execute(self, sql: str, parameters: Iterable[Any] = ...) -> 'DBCursor':
		...

	def fetchall(self) -> Any:
		...

class DBConn(Protocol):
	def cursor(self, cursorClass: Optional[type] = ...) -> DBCursor:
		...

@export
@dataclass
class Connection:
	c: DBConn

class QueryStep(Protocol):
	def render(self, prev: str) -> str:
		...

@export
@dataclass
class QueryPipeline:
	conn: DBCursor
	source_table: str
	steps: List[QueryStep]

	def chain(self, step: QueryStep) -> 'QueryPipeline':
		steps = self.steps.copy()
		steps.append(step)
		return QueryPipeline(self.conn, self.source_table, steps)

	def render(self) -> str:
		query = f'select * from {self.source_table}'
		for step in self.steps:
			query = step.render(query)
		return query

	def execute(self) -> Any:
		self.conn.execute(self.render())
		return self.conn.fetchall()

@dataclass
class Filter:
	exprs: List[str]

	def render(self, source: str) -> str:
		cond = ' and '.join(self.exprs)
		return f'select * from ({source}) where {cond}'

@dataclass
class Count:
	def render(self, source: str) -> str:
		return f'select count(*) from ({source})'

class JoinType(Enum):
	CROSS = "cross"
	LEFT = "left"

@dataclass
class Join:
	type: JoinType
	rhs: QueryPipeline

	def render(self, source: str) -> str:
		return f'select * from ({source}) {self.type.value} join ({self.rhs.render()})'

@export
@dataclass
class Grouping:
	names: List[str]
	computed: Dict[str, str]

@dataclass
class Aggregate:
	by: Grouping
	aggregations: Dict[str, str]

	def render(self, source: str) -> str:
		grouping_expr = ', '.join(self.by.names + list(self.by.computed.keys()))

		all_computations = {**self.by.computed, **self.aggregations}
		select_computed = [f'{c} as {name}' for name, c in all_computations.items()]

		select_expr = ', '.join(self.by.names + select_computed)
		return f'select {select_expr} from ({source}) group by {grouping_expr}'

@export
def connect_sqlite(connstring: str) -> Connection:
	return Connection(sqlite3.connect(connstring))

@export
def execute(conn: Connection, sql: str) -> None:
	cursor = conn.c.cursor()
	cursor.execute(sql)

@export
def get_table(conn: Connection, table: str) -> QueryPipeline:
	return QueryPipeline(conn.c.cursor(), table, [])

@export
def filter(query: QueryPipeline, expr: Expr) -> QueryPipeline:
	return query.chain(Filter([expr.render()]))

@export
def collect(query: QueryPipeline) -> Any:
	return query.execute()

@export
def count_rows(query: QueryPipeline) -> Number:
	query = query.chain(Count())
	data = query.execute()
	assert isinstance(data[0][0], int)
	return Number(data[0][0])

@export
def group(*by: Expr, **named_by: Expr) -> Grouping:
	return Grouping([expr.render() for expr in by], {name: expr.render() for name, expr in named_by.items()})

@export
def aggregate(query: QueryPipeline, by: Grouping, **computation: Expr) -> QueryPipeline:
	return query.chain(Aggregate(by, {name: c.render() for name, c in computation.items()}))

@export
def cross_join(query: QueryPipeline, rhs: QueryPipeline) -> QueryPipeline:
	return query.chain(Join(JoinType.CROSS, rhs))

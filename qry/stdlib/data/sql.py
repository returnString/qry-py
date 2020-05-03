from typing import Optional, Iterable, Any, List, Dict
from typing_extensions import Protocol
from dataclasses import dataclass
from enum import Enum

import sqlite3
import psycopg2

from qry.syntax import Expr
from qry.stdlib.export import export

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

@dataclass
class RenderState:
	alias_counter: int = 0

class QueryStep(Protocol):
	def render(self, prev: str, state: RenderState) -> str:
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

	def render(self, state: RenderState) -> str:
		query = f'select * from {self.source_table}'
		for step in self.steps:
			query = step.render(query, state)
		return query

	def execute(self) -> Any:
		state = RenderState()
		self.conn.execute(self.render(state))
		return self.conn.fetchall()

def render_subquery(source: str, state: RenderState) -> str:
	state.alias_counter += 1
	return f'({source}) qry_alias_{state.alias_counter}'

@dataclass
class Filter:
	exprs: List[str]

	def render(self, source: str, state: RenderState) -> str:
		cond = ' and '.join(self.exprs)
		return f'select * from {render_subquery(source, state)} where {cond}'

@dataclass
class Count:
	def render(self, source: str, state: RenderState) -> str:
		return f'select count(*) from {render_subquery(source, state)}'

class JoinType(Enum):
	CROSS = "cross"
	LEFT = "left"

@dataclass
class Join:
	type: JoinType
	rhs: QueryPipeline

	def render(self, source: str, state: RenderState) -> str:
		return f'select * from {render_subquery(source, state)} {self.type.value} join {render_subquery(self.rhs.render(state), state)}'

@export
@dataclass
class Grouping:
	names: List[str]
	computed: Dict[str, str]

@dataclass
class Aggregate:
	by: Grouping
	aggregations: Dict[str, str]

	def render(self, source: str, state: RenderState) -> str:
		grouping_expr = ', '.join(self.by.names + list(self.by.computed.keys()))

		all_computations = {**self.by.computed, **self.aggregations}
		select_computed = [f'{c} as {name}' for name, c in all_computations.items()]

		select_expr = ', '.join(self.by.names + select_computed)
		return f'select {select_expr} from {render_subquery(source, state)} group by {grouping_expr}'

@export
def connect_sqlite(connstring: str) -> Connection:
	return Connection(sqlite3.connect(connstring, isolation_level = None))

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
def count_rows(query: QueryPipeline) -> int:
	query = query.chain(Count())
	data = query.execute()
	assert isinstance(data[0][0], int)
	return data[0][0]

@export
def group(*by: Expr, **named_by: Expr) -> Grouping:
	return Grouping([expr.render() for expr in by], {name: expr.render() for name, expr in named_by.items()})

@export
def aggregate(query: QueryPipeline, by: Grouping, **computation: Expr) -> QueryPipeline:
	return query.chain(Aggregate(by, {name: c.render() for name, c in computation.items()}))

@export
def cross_join(query: QueryPipeline, rhs: QueryPipeline) -> QueryPipeline:
	return query.chain(Join(JoinType.CROSS, rhs))

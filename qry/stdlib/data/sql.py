from typing import Optional, Iterable, Any, List, Dict
from typing_extensions import Protocol
from dataclasses import dataclass
from enum import Enum

import sqlite3
import psycopg2
import pyarrow

from qry.syntax import *
from qry.stdlib.export import export
from qry.stdlib.core import Int, Float, String, Bool
from qry.stdlib import meta
from qry.environment import Environment

from .dataframe import DataFrame

class DBCursor(Protocol):
	def execute(self, sql: str, parameters: Iterable[Any] = ...) -> 'DBCursor':
		...

	def fetchall(self) -> Any:
		...

	description: Any
	rowcount: int

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
	cursor: DBCursor
	source_table: str
	steps: List[QueryStep]

	def chain(self, step: QueryStep) -> 'QueryPipeline':
		steps = self.steps.copy()
		steps.append(step)
		return QueryPipeline(self.cursor, self.source_table, steps)

	def render(self, state: RenderState) -> str:
		query = f'select * from {self.source_table}'
		for step in self.steps:
			query = step.render(query, state)
		return query

	def execute(self) -> DataFrame:
		state = RenderState()
		self.cursor.execute(self.render(state))
		column_names = [desc[0] for desc in self.cursor.description]
		rows = self.cursor.fetchall()
		column_data: List[Any] = [[] for c in column_names]

		for row_index, row in enumerate(rows):
			for col_index in range(0, len(column_names)):
				col = column_data[col_index]
				col.append(row[col_index])

		table = pyarrow.Table.from_arrays([pyarrow.array(a) for a in column_data], column_names)
		return DataFrame(table)

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

_sql_binop_translation = {
	BinaryOp.NOT_EQUAL: "<>",
}

def sql_interpret_value(value: Any) -> str:
	if isinstance(value, String):
		return f'\"{value.val}\""'
	elif isinstance(value, (Int, Float, Bool)):
		return str(value.val)

	raise Exception(f'unhandled value for sql: {value}')

def sql_interpret(env: Environment, expr: Expr) -> str:
	if isinstance(expr, BinaryOpExpr):
		op = _sql_binop_translation.get(expr.op.value, expr.op.value)
		return f'{sql_interpret(env, expr.lhs)} {op} {sql_interpret(env, expr.rhs)}'
	elif isinstance(expr, IdentExpr):
		return expr.value
	elif isinstance(expr, CallExpr):
		args = ', '.join([sql_interpret(env, a) for a in expr.positional_args])
		return f'{sql_interpret(env, expr.func)}({args})'
	elif isinstance(expr, (StringLiteral, IntLiteral, FloatLiteral, BoolLiteral)):
		return sql_interpret_value(expr.value)
	elif isinstance(expr, InterpolateExpr):
		return sql_interpret_value(meta.eval_in_env(expr, env))

	raise Exception(f'unhandled expr for sql: {expr}')

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
def execute(conn: Connection, sql: str) -> int:
	cursor = conn.c.cursor()
	cursor.execute(sql)
	return cursor.rowcount

@export
def get_table(conn: Connection, table: str) -> QueryPipeline:
	return QueryPipeline(conn.c.cursor(), table, [])

@export
def filter(_env: Environment, query: QueryPipeline, expr: Expr) -> QueryPipeline:
	return query.chain(Filter([sql_interpret(_env, expr)]))

@export
def collect(query: QueryPipeline) -> DataFrame:
	return query.execute()

@export
def group(_env: Environment, *by: Expr, **named_by: Expr) -> Grouping:
	return Grouping(
		[sql_interpret(_env, expr) for expr in by],
		{name: sql_interpret(_env, expr)
		for name, expr in named_by.items()},
	)

@export
def aggregate(_env: Environment, query: QueryPipeline, by: Grouping, **computation: Expr) -> QueryPipeline:
	return query.chain(Aggregate(by, {name: sql_interpret(_env, c) for name, c in computation.items()}))

@export
def cross_join(query: QueryPipeline, rhs: QueryPipeline) -> QueryPipeline:
	return query.chain(Join(JoinType.CROSS, rhs))

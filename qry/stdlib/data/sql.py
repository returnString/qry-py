from typing import Optional, Iterable, Any, List, Dict, Tuple, Union
from typing_extensions import Protocol
from dataclasses import dataclass
from enum import Enum

import pyarrow

from qry.common import export
from qry.lang import *
from qry.runtime import Environment, QryRuntimeError, InterpreterHooks

from .dataframe import DataFrame

qry_hooks: InterpreterHooks

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
	env: Environment
	expr: Expr

	def render(self, source: str, state: RenderState) -> str:
		return f'select * from {render_subquery(source, state)} where {sql_interpret(self.env, self.expr)}'

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
	env: Environment
	names: List[Expr]
	computed: Dict[str, Expr]

@dataclass
class Aggregate:
	env: Environment
	by: Grouping
	aggregations: Dict[str, Expr]

	def render(self, source: str, state: RenderState) -> str:
		names = [sql_interpret(self.by.env, e, constrain_to = IdentExpr) for e in self.by.names]
		grouping_expr = ', '.join(names + list(self.by.computed.keys()))

		all_computations = {**self.by.computed, **self.aggregations}
		select_computed = [f'{sql_interpret(self.env, c)} as {name}' for name, c in all_computations.items()]

		select_expr = ', '.join(names + select_computed)
		return f'select {select_expr} from {render_subquery(source, state)} group by {grouping_expr}'

@dataclass
class Select:
	env: Environment
	selection: List[Expr]
	computed: Dict[str, Expr]

	def render(self, source: str, state: RenderState) -> str:
		names = [sql_interpret(self.env, e, constrain_to = IdentExpr) for e in self.selection]
		select_computed = [f'{sql_interpret(self.env, c)} as {name}' for name, c in self.computed.items()]
		select_expr = ', '.join(names + select_computed)
		return f'select {select_expr} from {render_subquery(source, state)}'

_sql_binop_translation = {
	BinaryOp.EQUAL: '=',
	BinaryOp.NOT_EQUAL: '<>',
	BinaryOp.AND: 'and',
	BinaryOp.OR: 'or',
}

def sql_interpret_value(value: Any) -> str:
	if isinstance(value, String):
		return f'\'{value.val}\''
	elif isinstance(value, (Int, Float, Bool)):
		return str(value.val)

	raise Exception(f'unhandled value for sql: {value}')

def sql_interpret(env: Environment, expr: Expr, constrain_to: Union[type, Tuple[type, ...]] = (Expr, )) -> str:
	if not isinstance(expr, constrain_to):
		raise QryRuntimeError(f'expected expr of type: {constrain_to}')

	if isinstance(expr, BinaryOpExpr):
		op = _sql_binop_translation.get(expr.op, expr.op.value)
		return f'{sql_interpret(env, expr.lhs)} {op} {sql_interpret(env, expr.rhs)}'
	elif isinstance(expr, IdentExpr):
		return expr.value
	elif isinstance(expr, CallExpr):
		args = ', '.join([sql_interpret(env, a) for a in expr.positional_args])
		return f'{sql_interpret(env, expr.func)}({args})'
	elif isinstance(expr, (StringLiteral, IntLiteral, FloatLiteral, BoolLiteral)):
		return sql_interpret_value(expr.value)
	elif isinstance(expr, InterpolateExpr):
		return sql_interpret_value(qry_hooks.eval_in_env(expr, env))

	raise Exception(f'unhandled expr for sql: {expr}')

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
	return query.chain(Filter(_env, expr))

@export
def collect(query: QueryPipeline) -> DataFrame:
	return query.execute()

@export
def group(_env: Environment, *by: Expr, **named_by: Expr) -> Grouping:
	return Grouping(_env, list(by), named_by)

@export
def aggregate(_env: Environment, query: QueryPipeline, by: Grouping, **computation: Expr) -> QueryPipeline:
	return query.chain(Aggregate(_env, by, computation))

@export
def cross_join(query: QueryPipeline, rhs: QueryPipeline) -> QueryPipeline:
	return query.chain(Join(JoinType.CROSS, rhs))

@export
def mutate(_env: Environment, query: QueryPipeline, **computation: Expr) -> QueryPipeline:
	return query.chain(Select(_env, [], computation))

@export
def select(_env: Environment, query: QueryPipeline, *columns: Expr) -> QueryPipeline:
	return query.chain(Select(_env, list(columns), {}))

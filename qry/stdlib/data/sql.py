from typing import Optional, Iterable, Any, List, Dict, Tuple, Union, Callable
from typing_extensions import Protocol
from dataclasses import dataclass, field
from enum import Enum, auto

import pyarrow

from qry.common import export
from qry.lang import Expr, IdentExpr
from qry.runtime import Environment, QryRuntimeError

from .dataframe import DataFrame
from .sql_codegen import SQLExpressionTranslator
from .sql_connection import Connection, DBCursor, SQLExpression

def metadata_from_typecode_lookup(types: Dict[Any, type]) -> Any:
	def _get_type(typecode: Any) -> type:
		ret = types.get(typecode)
		if not ret:
			raise QryRuntimeError(f'unhandled typecode: {typecode}')
		return ret

	def _get_table_metadata(conn: Connection, table: str) -> Dict[str, type]:
		# FIXME: injection
		cursor = conn.c.cursor()
		cursor.execute(f'select * from {table} limit 0')
		cursor.fetchall()
		return {desc[0]: _get_type(desc[1]) for desc in cursor.description}

	return _get_table_metadata

@dataclass
class RenderStateCounter:
	_alias: int

@dataclass
class RenderState:
	conn: Connection
	query: str
	columns: Dict[str, type]
	counter: RenderStateCounter

	def substate(self) -> 'RenderState':
		return RenderState(self.conn, '', {}, self.counter)

	def copy(self, new_query: str, columns: Dict[str, type]) -> 'RenderState':
		assert len(columns)
		return RenderState(self.conn, new_query, columns, self.counter)

	def subquery(self) -> str:
		self.counter._alias += 1
		return f'({self.query}) qry_{self.counter._alias}'

	def translator(self, env: Environment) -> SQLExpressionTranslator:
		return SQLExpressionTranslator(self.conn, env, self.columns)

class QueryStep(Protocol):
	def render(self, state: RenderState) -> RenderState:
		...

@export
@dataclass
class QueryPipeline:
	conn: Connection
	steps: List[QueryStep]

	def chain(self, step: QueryStep) -> 'QueryPipeline':
		steps = self.steps.copy()
		steps.append(step)
		return QueryPipeline(self.conn, steps)

	def render(self, parent_state: RenderState) -> RenderState:
		state = parent_state.substate()
		for step in self.steps:
			state = step.render(state)
		return state

	def execute(self) -> DataFrame:
		state = self.render(RenderState(self.conn, '', {}, RenderStateCounter(0)))
		cursor = self.conn.c.cursor()
		cursor.execute(state.query)
		column_names = [desc[0] for desc in cursor.description]
		rows = cursor.fetchall()
		column_data: List[Any] = [[] for c in column_names]

		for row_index, row in enumerate(rows):
			for col_index in range(0, len(column_names)):
				col = column_data[col_index]
				col.append(row[col_index])

		table = pyarrow.Table.from_arrays([pyarrow.array(a) for a in column_data], column_names)
		return DataFrame(table)

@dataclass
class Filter:
	env: Environment
	expr: Expr

	def render(self, state: RenderState) -> RenderState:
		translator = state.translator(self.env)
		filter_expr = translator.eval(self.expr)
		return state.copy(f'select * from {state.subquery()} where {filter_expr.text}', state.columns)

@dataclass
class Count:
	def render(self, state: RenderState) -> RenderState:
		return state.copy(f'select count(*) from {state.subquery()}', {})

class JoinType(Enum):
	CROSS = "cross"
	LEFT = "left"

@dataclass
class Join:
	type: JoinType
	rhs: QueryPipeline

	def render(self, state: RenderState) -> RenderState:
		join_state = self.rhs.render(state.substate())
		return state.copy(f'select * from {state.subquery()} {self.type.value} join {join_state.subquery()}', {
			**state.columns,
			**join_state.columns,
		})

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

	def render(self, state: RenderState) -> RenderState:
		grouping_translator = state.translator(self.by.env)
		grouping_col_details = [grouping_translator.eval(e, constrain_to = IdentExpr) for e in self.by.names]
		names = [c.text for c in grouping_col_details]
		grouping_expr = ', '.join(names + list(self.by.computed.keys()))

		all_computations = {**self.by.computed, **self.aggregations}

		computed_translator = state.translator(self.env)
		computed_col_details = {name: computed_translator.eval(c) for name, c in all_computations.items()}
		select_computed = [f'{c.text} as {name}' for name, c in computed_col_details.items()]

		select_expr = ', '.join(names + select_computed)
		return state.copy(
			f'select {select_expr} from {state.subquery()} group by {grouping_expr}', {
			**{c.text: c.type
			for c in grouping_col_details},
			**{name: c.type
			for name, c in computed_col_details.items()},
			})

@dataclass
class Select:
	env: Environment
	selection: List[Expr]
	computed: Dict[str, Expr]

	def render(self, state: RenderState) -> RenderState:
		translator = state.translator(self.env)
		if self.selection:
			selection_details = [translator.eval(e, constrain_to = IdentExpr) for e in self.selection]
			names = [s.text for s in selection_details]
		else:
			selection_details = [SQLExpression(t, name) for name, t in state.columns.items()]
			names = list(state.columns.keys())

		computed_col_details = {name: translator.eval(c) for name, c in self.computed.items()}
		select_computed = [f'{c.text} as {name}' for name, c in computed_col_details.items()]
		select_expr = ', '.join(names + select_computed)

		return state.copy(f'select {select_expr} from {state.subquery()}', {
			**{s.text: s.type
			for s in selection_details},
			**{name: c.type
			for name, c in computed_col_details.items()},
		})

@dataclass
class From:
	table: str
	columns: Dict[str, type]

	def render(self, state: RenderState) -> RenderState:
		names = ', '.join(self.columns.keys())
		return state.copy(f'select {names} from {self.table}', self.columns)

@export
def execute(conn: Connection, sql: str) -> int:
	cursor = conn.c.cursor()
	cursor.execute(sql)
	return cursor.rowcount

@export
def get_table(conn: Connection, table: str) -> QueryPipeline:
	metadata_func = conn.get_table_metadata
	metadata = metadata_func(conn, table) # type: ignore
	return QueryPipeline(conn, [From(table, metadata)])

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

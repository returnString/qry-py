from typing import Any, Tuple, Union, Dict
from dataclasses import dataclass

from qry.common import export
from qry.runtime import Environment, QryRuntimeError, InterpreterHooks
from qry.lang import *
from qry.stdlib.ops import binop_lookup, unop_lookup

from .sql_connection import Connection, ColumnMetadata

_sql_binop_symbol_overrides = {
	BinaryOp.EQUAL: '=',
	BinaryOp.NOT_EQUAL: '<>',
	BinaryOp.AND: 'and',
	BinaryOp.OR: 'or',
}

_sql_binop_signature_symbol_overrides = {
	(BinaryOp.ADD, Int, Int): '+', # TODO: remove later; this is just to shut mypy up and not infer specific types
	(BinaryOp.ADD, String, String): '||',
}

def sql_interpret_value(value: Any) -> str:
	if isinstance(value, String):
		return f'\'{value.val}\''
	elif isinstance(value, (Int, Float, Bool)):
		return str(value.val)

	raise Exception(f'unhandled value for sql: {value}')

def sql_interpret(
	conn: Connection,
	env: Environment,
	expr: Expr,
	columns: Dict[str, ColumnMetadata],
	constrain_to: Union[type, Tuple[type, ...]] = (Expr, ),
) -> Tuple[ColumnMetadata, str]:
	if not isinstance(expr, constrain_to):
		raise QryRuntimeError(f'expected expr of type: {constrain_to}')

	# TODO: actually return useful metadata here
	if isinstance(expr, BinaryOpExpr):
		lhs_type, lhs = sql_interpret(conn, env, expr.lhs, columns)
		rhs_type, rhs = sql_interpret(conn, env, expr.rhs, columns)

		if conn.rewrite_binop is not None:
			rewrite_func = conn.rewrite_binop
			ret = rewrite_func(expr.op, lhs_type, lhs, rhs_type, rhs)
			if ret:
				return ret

		default_symbol = _sql_binop_symbol_overrides.get(expr.op, expr.op.value)
		symbol = _sql_binop_signature_symbol_overrides.get((expr.op, lhs_type.type, rhs_type.type), default_symbol)

		method = binop_lookup[expr.op]
		_, func = method.resolve([lhs_type.type, rhs_type.type], allow_default = False)

		return (ColumnMetadata(func.return_type), f'{lhs} {symbol} {rhs}')
	elif isinstance(expr, IdentExpr):
		column_value = columns[expr.value]
		return (column_value, expr.value)
	elif isinstance(expr, CallExpr):
		arg_details = [sql_interpret(conn, env, a, columns) for a in expr.positional_args]
		args = ', '.join([a[1] for a in arg_details])
		assert isinstance(expr.func, IdentExpr)
		func_name = expr.func.value
		return (ColumnMetadata(Int), f'{func_name}({args})')
	elif isinstance(expr, (StringLiteral, IntLiteral, FloatLiteral, BoolLiteral)):
		return (ColumnMetadata(type(expr.value)), sql_interpret_value(expr.value))
	elif isinstance(expr, InterpolateExpr):
		value = env.eval(expr)
		return (ColumnMetadata(type(value)), sql_interpret_value(value))

	raise Exception(f'unhandled expr for sql: {expr}')

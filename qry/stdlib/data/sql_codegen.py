from typing import Any, Tuple, Union, Dict
from dataclasses import dataclass

from qry.common import export
from qry.runtime import Environment, QryRuntimeError, InterpreterHooks
from qry.lang import *
from qry.stdlib.ops import binop_lookup, unop_lookup

@dataclass
class ColumnMetadata:
	type: type

_sql_binop_symbol_overrides = {
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

def sql_interpret(
	env: Environment,
	expr: Expr,
	columns: Dict[str, ColumnMetadata],
	constrain_to: Union[type, Tuple[type, ...]] = (Expr, ),
) -> Tuple[ColumnMetadata, str]:
	if not isinstance(expr, constrain_to):
		raise QryRuntimeError(f'expected expr of type: {constrain_to}')

	# TODO: actually return useful metadata here
	if isinstance(expr, BinaryOpExpr):
		symbol = _sql_binop_symbol_overrides.get(expr.op, expr.op.value)
		lhs_type, lhs = sql_interpret(env, expr.lhs, columns)
		rhs_type, rhs = sql_interpret(env, expr.rhs, columns)
		method = binop_lookup[expr.op]
		func = method.resolve([lhs_type.type, rhs_type.type])
		return (ColumnMetadata(Int), f'{lhs} {symbol} {rhs}')
	elif isinstance(expr, IdentExpr):
		return (ColumnMetadata(Int), expr.value)
	elif isinstance(expr, CallExpr):
		arg_details = [sql_interpret(env, a, columns) for a in expr.positional_args]
		args = ', '.join([a[1] for a in arg_details])
		_, func_name = sql_interpret(env, expr.func, columns)
		return (ColumnMetadata(Int), f'{func_name}({args})')
	elif isinstance(expr, (StringLiteral, IntLiteral, FloatLiteral, BoolLiteral)):
		return (ColumnMetadata(Int), sql_interpret_value(expr.value))
	elif isinstance(expr, InterpolateExpr):
		return (ColumnMetadata(Int), sql_interpret_value(env.eval(expr)))

	raise Exception(f'unhandled expr for sql: {expr}')

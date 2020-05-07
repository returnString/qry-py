from typing import Any, Tuple, Union

from qry.common import export
from qry.runtime import Environment, QryRuntimeError, InterpreterHooks
from qry.lang import *

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
		return sql_interpret_value(env.eval(expr))

	raise Exception(f'unhandled expr for sql: {expr}')

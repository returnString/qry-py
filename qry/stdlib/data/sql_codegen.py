from typing import Any, Tuple, Union, Dict, cast
from dataclasses import dataclass

from qry.common import export
from qry.runtime import Environment, QryRuntimeError, InterpreterHooks
from qry.lang import *
from qry.stdlib.ops import binop_lookup, unop_lookup

from .sql_connection import Connection, SQLExpression

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

def make_literal_eval(literal_type: type) -> Any:
	def literal_eval(_: Any, expr: Any) -> SQLExpression:
		return SQLExpression(type(expr.value), sql_interpret_value(expr.value))

	return literal_eval

@dataclass
class SQLExpressionTranslator:
	conn: Connection
	env: Environment
	columns: Dict[str, type]

	def eval(self, expr: Expr, constrain_to: Union[type, Tuple[type, ...]] = (Expr, )) -> SQLExpression:
		if not isinstance(expr, constrain_to):
			raise QryRuntimeError(f'expected expr of type: {constrain_to}')

		eval_func = getattr(self, f'_eval_{type(expr).__name__}')
		ret = cast(SQLExpression, eval_func(expr))
		return ret

	def _eval_BinaryOpExpr(self, expr: BinaryOpExpr) -> SQLExpression:
		lhs = self.eval(expr.lhs)
		rhs = self.eval(expr.rhs)

		if self.conn.rewrite_binop is not None:
			rewrite_func = self.conn.rewrite_binop
			ret = rewrite_func(expr.op, lhs, rhs)
			if ret:
				return ret

		default_symbol = _sql_binop_symbol_overrides.get(expr.op, expr.op.value)
		symbol = _sql_binop_signature_symbol_overrides.get((expr.op, lhs.type, rhs.type), default_symbol)

		method = binop_lookup[expr.op]
		_, func = method.resolve([lhs.type, rhs.type], allow_default = False)

		return SQLExpression(func.return_type, f'{lhs.text} {symbol} {rhs.text}')

	def _eval_IdentExpr(self, expr: IdentExpr) -> SQLExpression:
		column_value = self.columns[expr.value]
		return SQLExpression(column_value, expr.value)

	def _eval_CallExpr(self, expr: CallExpr) -> SQLExpression:
		arg_details = [self.eval(a) for a in expr.positional_args]
		args = ', '.join([a.text for a in arg_details])
		assert isinstance(expr.func, IdentExpr)
		func_name = expr.func.value
		# FIXME: sort function types
		return SQLExpression(Int, f'{func_name}({args})')

	def _eval_InterpolateExpr(self, expr: InterpolateExpr) -> SQLExpression:
		value = self.env.eval(expr)
		return SQLExpression(type(value), sql_interpret_value(value))

	_eval_StringLiteral = make_literal_eval(StringLiteral)
	_eval_IntLiteral = make_literal_eval(IntLiteral)
	_eval_FloatLiteral = make_literal_eval(FloatLiteral)
	_eval_BoolLiteral = make_literal_eval(BoolLiteral)

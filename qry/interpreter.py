from typing import Dict, Any
import operator
from dataclasses import dataclass

from .syntax import *

@dataclass
class Null:
	def __str__(self) -> str:
		return 'null'

null = Null()

_eager_binop_lookup = {
	BinaryOp.ADD: operator.add,
	BinaryOp.SUBTRACT: operator.sub,
	BinaryOp.DIVIDE: operator.truediv,
	BinaryOp.MULTIPLY: operator.mul,
	BinaryOp.EQUAL: operator.eq,
	BinaryOp.NOT_EQUAL: operator.ne,
}

_eager_unop_lookup = {
	UnaryOp.NEGATE_LOGICAL: operator.not_,
	UnaryOp.NEGATE_ARITH: operator.neg,
}

class InterpreterError(Exception):
	pass

class Interpreter:
	state: Dict[str, Any] = dict()

	def eval(self, expr: Expr) -> Any:
		eval_func = getattr(self, f'eval_{type(expr).__name__}')
		return eval_func(expr)

	def eval_BinaryOpExpr(self, expr: BinaryOpExpr) -> Any:
		if expr.op == BinaryOp.LASSIGN:
			rhs = self.eval(expr.rhs)
			assert isinstance(expr.lhs, IdentExpr)
			self.state[expr.lhs.value] = rhs
			return rhs
		elif expr.op == BinaryOp.RASSIGN:
			lhs = self.eval(expr.lhs)
			assert isinstance(expr.rhs, IdentExpr)
			self.state[expr.rhs.value] = lhs
			return lhs
		else:
			lhs = self.eval(expr.lhs)
			rhs = self.eval(expr.rhs)
			return _eager_binop_lookup[expr.op](lhs, rhs)

		raise InterpreterError(f'unsupported binary op: {expr.op}')

	def eval_UnaryOpExpr(self, expr: UnaryOpExpr) -> Any:
		arg = self.eval(expr.arg)
		return _eager_unop_lookup[expr.op](arg)

		raise InterpreterError(f'unsupported unary op: {expr.op}')

	def eval_BoolLiteral(self, expr: BoolLiteral) -> Any:
		return expr.value

	def eval_IntLiteral(self, expr: IntLiteral) -> Any:
		return expr.value

	def eval_FloatLiteral(self, expr: FloatLiteral) -> Any:
		return expr.value

	def eval_StringLiteral(self, expr: StringLiteral) -> Any:
		return expr.value

	def eval_IdentExpr(self, expr: IdentExpr) -> Any:
		if expr.value not in self.state:
			raise InterpreterError(f'not found: {expr.value}')

		return self.state[expr.value]

	def eval_NullLiteral(self, expr: NullLiteral) -> Any:
		return null

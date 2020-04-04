from typing import Dict, Any, List
import operator

from .syntax import *
from .runtime import *

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
	global_env: Environment

	def __init__(self) -> None:
		self.global_env = Environment('global', dict())

	def eval(self, expr: Expr) -> Any:
		return self.eval_in_env(expr, self.global_env)

	def eval_in_env(self, expr: Expr, env: Environment) -> Any:
		eval_func = getattr(self, f'eval_{type(expr).__name__}')
		return eval_func(expr, env)

	def eval_BinaryOpExpr(self, expr: BinaryOpExpr, env: Environment) -> Any:
		if expr.op == BinaryOp.LASSIGN:
			rhs = self.eval_in_env(expr.rhs, env)
			assert isinstance(expr.lhs, IdentExpr)
			env.state[expr.lhs.value] = rhs
			return rhs
		elif expr.op == BinaryOp.RASSIGN:
			lhs = self.eval_in_env(expr.lhs, env)
			assert isinstance(expr.rhs, IdentExpr)
			env.state[expr.rhs.value] = lhs
			return lhs
		else:
			lhs = self.eval_in_env(expr.lhs, env)
			rhs = self.eval_in_env(expr.rhs, env)
			return _eager_binop_lookup[expr.op](lhs, rhs)

		raise InterpreterError(f'unsupported binary op: {expr.op}')

	def eval_UnaryOpExpr(self, expr: UnaryOpExpr, env: Environment) -> Any:
		arg = self.eval_in_env(expr.arg, env)
		return _eager_unop_lookup[expr.op](arg)

		raise InterpreterError(f'unsupported unary op: {expr.op}')

	def eval_BoolLiteral(self, expr: BoolLiteral, env: Environment) -> Any:
		return expr.value

	def eval_IntLiteral(self, expr: IntLiteral, env: Environment) -> Any:
		return expr.value

	def eval_FloatLiteral(self, expr: FloatLiteral, env: Environment) -> Any:
		return expr.value

	def eval_StringLiteral(self, expr: StringLiteral, env: Environment) -> Any:
		return expr.value

	def eval_IdentExpr(self, expr: IdentExpr, env: Environment) -> Any:
		if expr.value not in env.state:
			raise InterpreterError(f'not found: {expr.value}')

		return env.state[expr.value]

	def eval_NullLiteral(self, expr: NullLiteral, env: Environment) -> Any:
		return Null()

	def eval_FuncExpr(self, expr: FuncExpr, env: Environment) -> Any:
		return Function(expr.args, expr.body, env.child_env('func_closure'))

	def eval_CallExpr(self, expr: CallExpr, env: Environment) -> Any:
		func = self.eval_in_env(expr.func, env)

		arg_values = [self.eval_in_env(e, env) for e in expr.args]

		if isinstance(func, Function):
			func_env = func.environment.child_env('exec')
			for arg_name, arg_value in zip(func.args, arg_values):
				func_env.state[arg_name] = arg_value

			ret = None
			for e in func.body:
				ret = self.eval_in_env(e, func_env)

			return ret
		elif isinstance(func, BuiltinFunction):
			return func.func(*arg_values)

		raise InterpreterError('invalid function')

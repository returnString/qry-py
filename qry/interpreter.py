from typing import Dict, Any, List
import operator
import inspect

from .syntax import *
from .runtime import *
from .stdlib.core import CoreLib
from .stdlib.math import MathLib

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
	root_env: Environment
	global_env: Environment

	def __init__(self) -> None:
		self.root_env = Environment('root', dict())
		self.global_env = self.root_env.child_env('global')
		self.load_library(CoreLib(), True)
		self.load_library(MathLib(), False)

	def eval(self, expr: Expr) -> Any:
		return self.eval_in_env(expr, self.global_env)

	def load_library(self, lib_instance: Any, attach: bool) -> None:
		public_methods = [(name, m) for name, m in inspect.getmembers(lib_instance, inspect.ismethod)
			if not name.startswith('_')]

		public_types = [(name, m) for name, m in inspect.getmembers(lib_instance, inspect.isclass)
			if not name.startswith('_')]

		lib_name = type(lib_instance).__name__.lower().replace('lib', '')
		if lib_name is None:
			raise InterpreterError('failed to retrieve lib name')

		funcs = {name: BuiltinFunction.from_func(func) for name, func in public_methods}
		types = {name: type for name, type in public_types}

		lib_state = {**funcs, **types}

		lib_env = self.root_env.child_env(lib_name)
		lib_env.state.update(lib_state)

		lib = Library(lib_env)
		self.global_env.state[lib_name] = lib

		if attach:
			self.global_env.state.update(lib_state)

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
		elif expr.op == BinaryOp.ACCESS:
			lhs = self.eval_in_env(expr.lhs, env)
			assert isinstance(expr.rhs, IdentExpr)
			assert isinstance(lhs, Library)
			return self._find_in_env(lhs.environment, expr.rhs)
		else:
			lhs = self.eval_in_env(expr.lhs, env)
			rhs = self.eval_in_env(expr.rhs, env)
			return _eager_binop_lookup[expr.op](lhs, rhs)

		raise InterpreterError(f'unsupported binary op: {expr.op}')

	def _find_in_env(self, env: Environment, ident: IdentExpr) -> Any:
		if ident.value not in env.state:
			raise InterpreterError(f'not found: {ident.value}')

		return env.state[ident.value]

	def eval_UnaryOpExpr(self, expr: UnaryOpExpr, env: Environment) -> Any:
		arg = self.eval_in_env(expr.arg, env)
		return _eager_unop_lookup[expr.op](arg)

	def eval_BoolLiteral(self, expr: BoolLiteral, env: Environment) -> Any:
		return expr.value

	def eval_IntLiteral(self, expr: IntLiteral, env: Environment) -> Any:
		return expr.value

	def eval_FloatLiteral(self, expr: FloatLiteral, env: Environment) -> Any:
		return expr.value

	def eval_StringLiteral(self, expr: StringLiteral, env: Environment) -> Any:
		return expr.value

	def eval_IdentExpr(self, expr: IdentExpr, env: Environment) -> Any:
		return self._find_in_env(env, expr)

	def eval_NullLiteral(self, expr: NullLiteral, env: Environment) -> Any:
		return Null()

	def eval_FuncExpr(self, expr: FuncExpr, env: Environment) -> Any:
		args = [Argument(name, self.eval_in_env(type, env)) for name, type in expr.args.items()]
		return Function(args, expr.body, env.child_env('func_closure'))

	def eval_CallExpr(self, expr: CallExpr, env: Environment) -> Any:
		func = self.eval_in_env(expr.func, env)

		provided_values = [self.eval_in_env(e, env) for e in expr.args]

		if isinstance(func, Function):
			func_env = func.environment.child_env('exec')
			for arg, provided_value in zip(func.args, provided_values):
				func_env.state[arg.name] = provided_value

			ret = None
			for e in func.body:
				ret = self.eval_in_env(e, func_env)

			return ret
		elif isinstance(func, BuiltinFunction):
			return func.func(*provided_values)

		raise InterpreterError(f'invalid function: {func}')

from typing import Dict, Any, List
from types import ModuleType, FunctionType
import copy

from qry.common import get_all_exported_objs
from qry.stdlib import core, ops, meta, data
from qry.lang import *
from qry.lang import coretypes

from qry.runtime import Environment, QryRuntimeError, Library, to_py, from_py
from qry.runtime import Method, Function, BuiltinFunction, Argument, ArgumentMode

class Interpreter:
	root_env: Environment
	library_env: Environment
	global_env: Environment

	def __init__(self) -> None:
		self.root_env = Environment('root', dict(), self)
		self.library_env = Environment('libraries', dict(), self)
		self.global_env = self.root_env.child_env('global')
		self.load_library(coretypes, True)
		self.load_library(core, True)
		self.load_library(ops, True)
		self.load_library(meta, False)
		self.load_library(data, False)

	def eval(self, expr: Expr) -> Any:
		return self.eval_in_env(expr, self.global_env)

	def _get_lib_name(self, lib_instance: ModuleType) -> str:
		lib_name = lib_instance.__name__.split('.')[-1]
		if lib_name is None:
			raise QryRuntimeError('failed to retrieve lib name')
		return lib_name

	def load_library(self, lib_module: ModuleType, attach_global: bool) -> None:
		lib_name = self._get_lib_name(lib_module)

		lib_state = {}
		export_list = get_all_exported_objs(lib_module)
		for obj in export_list:
			name = obj.__name__
			if isinstance(obj, FunctionType):
				obj = BuiltinFunction.from_func(obj)

			lib_state[name] = obj

		lib_env = self.root_env.child_env(lib_name)
		lib_env.state.update(lib_state)

		lib = Library(lib_env)
		self.library_env.state[lib_name] = lib

		if attach_global:
			self.attach_library(self.global_env, lib)

	def attach_library(self, env: Environment, lib: Library) -> None:
		env.state.update(lib.environment.state)

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
		elif expr.op == BinaryOp.PIPE:
			assert isinstance(expr.rhs, CallExpr)
			new_rhs = copy.copy(expr.rhs)
			new_rhs.positional_args.insert(0, expr.lhs)
			return self.eval_in_env(new_rhs, env)
		else:
			lhs = self.eval_in_env(expr.lhs, env)
			rhs = self.eval_in_env(expr.rhs, env)
			method = ops.binop_lookup[expr.op]
			return method.call([lhs, rhs])

		raise QryRuntimeError(f'unsupported binary op: {expr.op}')

	def _find_in_env(self, env: Environment, ident: IdentExpr) -> Any:
		if ident.value not in env.state:
			raise QryRuntimeError(f'not found: {ident.value}')

		return env.state[ident.value]

	def eval_UnaryOpExpr(self, expr: UnaryOpExpr, env: Environment) -> Any:
		arg = self.eval_in_env(expr.arg, env)
		method = ops.unop_lookup[expr.op]
		return method.call([arg])

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

	def _create_arg(self, name: str, arg_type_expr: Expr, env: Environment) -> Argument:
		arg_type = self.eval_in_env(arg_type_expr, env)
		return Argument(name, arg_type, arg_type is not Expr, ArgumentMode.STANDARD, False)

	def eval_FuncExpr(self, expr: FuncExpr, env: Environment) -> Any:
		args = [self._create_arg(name, type, env) for name, type in expr.args.items()]
		return_type = self.eval_in_env(expr.return_type, env)
		ret = Function(args, return_type, expr.body, env.child_env('func_closure'))
		if expr.name is not None:
			env.state[expr.name] = ret
		return ret

	def eval_CallExpr(self, expr: CallExpr, env: Environment) -> Any:
		target = self.eval_in_env(expr.func, env)

		method = None
		if isinstance(target, Method):
			method = target
			target = method.default_func
			func_args = method.default_func.args
		else:
			func_args = target.args

		if isinstance(target, Function):
			func_env = target.environment.child_env('exec')
			for arg, provided_expr in zip(func_args, expr.positional_args):
				if arg.eval_immediate:
					func_env.state[arg.name] = self.eval_in_env(provided_expr, env)
				else:
					func_env.state[arg.name] = provided_expr

			ret = None
			for e in target.body:
				ret = self.eval_in_env(e, func_env)

			return ret
		elif isinstance(target, BuiltinFunction):
			args: List[Any] = []
			if target.implicit_caller_env:
				args.append(env)

			type_args: List[Any] = []
			kwargs: Dict[str, Any] = {}

			def arg_eval_wrapper(arg: Argument, target: Expr) -> Any:
				ret = self.eval_in_env(target, env)
				if arg.convert_to_py:
					ret = to_py(ret)
				return ret

			for i, provided_expr in enumerate(expr.positional_args):
				arg = func_args[i]
				if arg.mode == ArgumentMode.VARARGS:
					remaining_args = expr.positional_args[i:]

					for vararg in remaining_args:
						if arg.eval_immediate:
							args.append(arg_eval_wrapper(arg, vararg))
						else:
							args.append(vararg)
					break
				elif arg.mode == ArgumentMode.TYPEPARAM:
					arg_type = arg_eval_wrapper(arg, provided_expr)
					type_args.append(arg_type)
				else:
					if arg.eval_immediate:
						args.append(arg_eval_wrapper(arg, provided_expr))
					else:
						args.append(provided_expr)

			if func_args:
				last_arg = func_args[-1]
				if last_arg.mode == ArgumentMode.KWARGS:
					if last_arg.eval_immediate:
						kwargs = {name: arg_eval_wrapper(last_arg, e) for name, e in expr.named_args.items()}
					else:
						kwargs = expr.named_args

			if method:
				ret = method.call(args, type_params = type_args)
			else:
				ret = target.func(*args, **kwargs)

			return from_py(ret)

		raise QryRuntimeError(f'invalid function: {target}')

	def eval_InterpolateExpr(self, expr: InterpolateExpr, env: Environment) -> Any:
		return self.eval_in_env(expr.contents, env)

	def eval_UseExpr(self, expr: UseExpr, env: Environment) -> Any:
		lib_env = self.library_env
		for lib_ident in expr.libs:
			lib = lib_env.state[lib_ident]
			assert isinstance(lib, Library)
			lib_env = lib.environment

		imports = lib_env.state.keys() if isinstance(expr.imports, UseWildcard) else expr.imports
		for ident in imports:
			env.state[ident] = lib_env.state[ident]

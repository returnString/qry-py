from typing import List, Any, Dict, Callable
from dataclasses import dataclass, field
import inspect

from .syntax import Expr, FuncExpr
from .environment import Environment
from .stdlib import meta

@dataclass
class Null:
	def __repr__(self) -> str:
		return 'null'

@dataclass
class Argument:
	name: str
	type: Any
	eval_immediate: bool

	def __repr__(self) -> str:
		return f'{self.name}: {self.type}'

@dataclass
class FunctionBase:
	args: List[Argument]

	def __repr__(self) -> str:
		return f'fn({", ".join([ repr(a) for a in self.args ])})'

@dataclass
class Function(FunctionBase):
	body: List[Expr]
	environment: Environment

def _py_arg(arg_spec: inspect.FullArgSpec, name: str) -> Argument:
	annotated_type = arg_spec.annotations[name]
	return Argument(name, annotated_type, annotated_type is not meta.Syntax)

@dataclass
class BuiltinFunction(FunctionBase):
	func: Callable[..., Any]
	implicit_caller_env: bool

	def __repr__(self) -> str:
		return '[builtin] ' + super().__repr__()

	@classmethod
	def from_func(cls, func: Callable[..., Any]) -> 'BuiltinFunction':
		arg_spec = inspect.getfullargspec(func)
		arg_names = arg_spec.args

		# skip self if handling bound method
		if arg_names and arg_names[0] == 'self':
			arg_names = arg_names[1:]

		implicit_caller_env = len(arg_names) > 0 and arg_names[0] == '_env'
		if implicit_caller_env:
			arg_names = arg_names[1:]

		args = [_py_arg(arg_spec, a) for a in arg_names]
		return cls(args, func, implicit_caller_env)

@dataclass
class Library:
	environment: Environment

	def __repr__(self) -> str:
		return f'library "{self.environment.name}" (object count: {len(self.environment.state)})'

from typing import List, Any, Dict, Callable
from dataclasses import dataclass, field
import inspect

from .syntax import Expr, FuncExpr

@dataclass
class Environment:
	name: str
	state: Dict[str, Any]

	def child_env(self, name: str) -> 'Environment':
		child_state = self.state.copy()
		return Environment(name, child_state)

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

@dataclass
class BuiltinFunction(FunctionBase):
	func: Callable[..., Any]

	def __repr__(self) -> str:
		return '[builtin] ' + super().__repr__()

	@classmethod
	def from_func(cls, func: Callable[..., Any]) -> 'BuiltinFunction':
		# skip self
		py_args = inspect.getfullargspec(func).args[1:]
		args = [Argument(a, 'Any', True) for a in py_args]
		return cls(args, func)

@dataclass
class Library:
	environment: Environment

	def __repr__(self) -> str:
		return f'library "{self.environment.name}" (object count: {len(self.environment.state)})'

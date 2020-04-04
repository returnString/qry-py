from typing import List, Any, Dict, Callable
from dataclasses import dataclass, field

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
class FunctionBase:
	args: List[str]

	def __repr__(self) -> str:
		return f'fn({", ".join(self.args)})'

@dataclass
class Function(FunctionBase):
	body: List[Expr]
	environment: Environment

@dataclass
class BuiltinFunction(FunctionBase):
	func: Callable[..., Any]

	def __repr__(self) -> str:
		return '[builtin] ' + super().__repr__()

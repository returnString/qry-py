from typing import List, Any, Dict
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
class Function:
	args: List[str]
	body: List[Expr]
	environment: Environment

	def __repr__(self) -> str:
		return f'fn({", ".join(self.args)})'

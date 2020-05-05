from typing import Any
from typing_extensions import Protocol

from qry.lang import Expr

from .environment import Environment
from .runtime import Library

class InterpreterHooks(Protocol):
	def eval_in_env(self, expr: Expr, env: Environment) -> Any:
		...

	def attach_library(self, env: Environment, library: Library) -> None:
		...

from typing import Any, Callable
from dataclasses import dataclass

from ..runtime import Environment
from ..syntax import Expr

@dataclass
class AST:
	root: Expr
	env: Environment

class MetaLib:
	def __init__(self, eval_in_env: Callable[[Expr, Environment], Any]) -> None:
		self._eval_in_env = eval_in_env

	# marker type for deferring evaluation of function arguments
	class Syntax(Expr):
		pass

	def get_ast(self, _env: Environment, expr: Syntax) -> AST:
		return AST(expr, _env)

	def eval_ast(self, ast: AST) -> Any:
		return self._eval_in_env(ast.root, ast.env)

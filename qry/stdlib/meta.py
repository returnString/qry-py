from typing import Any, Callable
from dataclasses import dataclass

from ..runtime import Environment
from ..syntax import Expr

from .export import export

@export
@dataclass
class AST:
	root: Expr
	env: Environment

	def __str__(self) -> str:
		return self.root.render()

# marker type for deferring evaluation of function arguments
@export
class Syntax(Expr):
	pass

_eval_in_env: Callable[[Expr, Environment], Any]

def init(eval_in_env: Callable[[Expr, Environment], Any]) -> None:
	global _eval_in_env
	_eval_in_env = eval_in_env

@export
def get_ast(_env: Environment, expr: Syntax) -> AST:
	return AST(expr, _env)

@export
def eval_ast(ast: AST) -> Any:
	return _eval_in_env(ast.root, ast.env)

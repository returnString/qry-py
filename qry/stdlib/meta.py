from typing import Any, Callable
from dataclasses import dataclass

from ..environment import Environment
from ..syntax import Expr

from .export import export
from .ops import to_string

@export
@dataclass
class AST:
	root: Expr
	env: Environment

@to_string
def ast_to_string(ast: AST) -> str:
	return ast.root.render()

eval_in_env: Callable[[Expr, Environment], Any]

def init(func: Callable[[Expr, Environment], Any]) -> None:
	global eval_in_env
	eval_in_env = func

@export
def get_ast(_env: Environment, expr: Expr) -> AST:
	return AST(expr, _env)

@export
def eval_ast(ast: AST) -> Any:
	return eval_in_env(ast.root, ast.env)

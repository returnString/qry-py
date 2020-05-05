from typing import Any
from dataclasses import dataclass

from qry.common import export
from qry.runtime import Environment, InterpreterHooks
from qry.lang import Expr

from qry.stdlib.ops import to_string

qry_hooks: InterpreterHooks

@export
@dataclass
class AST:
	root: Expr
	env: Environment

@export
def get_ast(_env: Environment, expr: Expr) -> AST:
	return AST(expr, _env)

@export
def eval_ast(ast: AST) -> Any:
	return qry_hooks.eval_in_env(ast.root, ast.env)

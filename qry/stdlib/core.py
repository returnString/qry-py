import builtins
from decimal import Decimal
from typing import Callable, Any

from ..environment import Environment
from .export import export

@export
class Number(Decimal):
	pass

@export
class String(str):
	pass

_attach_hook: Callable[..., None]

def init(attach_hook: Callable[..., None]) -> None:
	global _attach_hook
	_attach_hook = attach_hook

@export
def print(*text: String) -> None:
	builtins.print(*text)

@export
def attach(_env: Environment, library: Any) -> None:
	_attach_hook(_env, library)

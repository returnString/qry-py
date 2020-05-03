from decimal import Decimal
from dataclasses import dataclass
from typing import Union, Callable, Any

from qry.environment import Environment
from qry.stdlib.export import export

@export
class Number:
	val: Decimal

	def __init__(self, val: Union[Decimal, int, float]) -> None:
		self.val = Decimal(val)

@export
@dataclass
class String:
	val: str

@export
@dataclass
class Bool:
	val: bool

@export
class Null:
	pass

_attach_hook: Callable[..., None]

def init(attach_hook: Callable[..., None]) -> None:
	global _attach_hook
	_attach_hook = attach_hook

@export
def attach(_env: Environment, library: Any) -> None:
	_attach_hook(_env, library)

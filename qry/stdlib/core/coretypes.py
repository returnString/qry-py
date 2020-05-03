from dataclasses import dataclass
from typing import Union, Callable, Any

from qry.environment import Environment
from qry.stdlib.export import export

@export
@dataclass
class Int:
	val: int

@export
@dataclass
class Float:
	val: float

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

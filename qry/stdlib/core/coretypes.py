from dataclasses import dataclass
from typing import Union, Callable, Any

from qry.lang import Int, Float, String, Bool
from qry.runtime import Environment
from qry.common import export

_attach_hook: Callable[..., None]

def init(attach_hook: Callable[..., None]) -> None:
	global _attach_hook
	_attach_hook = attach_hook

@export
def attach(_env: Environment, library: Any) -> None:
	_attach_hook(_env, library)

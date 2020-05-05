from typing import Callable, Any

from qry.runtime import Environment
from qry.common import export

_attach_hook: Callable[..., None]

def init(attach_hook: Callable[..., None]) -> None:
	global _attach_hook
	_attach_hook = attach_hook

@export
def attach(_env: Environment, library: Any) -> None:
	_attach_hook(_env, library)

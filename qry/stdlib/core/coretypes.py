from typing import Callable, Any

from qry.runtime import Environment, Library
from qry.common import export

@export
def attach(_env: Environment, library: Library) -> None:
	_env.interpreter_hooks.attach_library(_env, library)

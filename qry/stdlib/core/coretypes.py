from typing import Callable, Any

from qry.runtime import Environment, InterpreterHooks
from qry.common import export

qry_hooks: InterpreterHooks

@export
def attach(_env: Environment, library: Any) -> None:
	qry_hooks.attach_library(_env, library)

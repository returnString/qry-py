from typing import Any
from dataclasses import dataclass

from qry.lang import String, Float, Int, Bool, Null
from qry.common import is_exported

from .environment import Environment
from .error import QryRuntimeError

def to_py(obj: Any) -> Any:
	if isinstance(obj, (String, Int, Float, Bool)):
		return obj.val
	elif isinstance(obj, Null):
		return None

	return obj

def from_py(obj: Any) -> Any:
	if is_exported(type(obj)):
		return obj
	elif isinstance(obj, bool):
		return Bool(obj)
	if isinstance(obj, int):
		return Int(obj)
	if isinstance(obj, float):
		return Float(obj)
	elif isinstance(obj, str):
		return String(obj)
	elif obj is None:
		return Null()

	raise QryRuntimeError(f'returning unsupported type ({type(obj)}) to qry: {obj}')

@dataclass
class Library:
	environment: Environment

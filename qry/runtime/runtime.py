from typing import Any, Callable
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

@dataclass
class TypeTranslator:
	qry_type: type
	translate_func: Callable[[Any], Any]

_qry_type_map = {
	str: TypeTranslator(String, lambda x: String(x)),
	bool: TypeTranslator(Bool, lambda x: Bool(x)),
	int: TypeTranslator(Int, lambda x: Int(x)),
	float: TypeTranslator(Float, lambda x: Float(x)),
	type(None): TypeTranslator(Null, lambda _: Null()),
}

_py_type_map = {translator.qry_type: py_type for py_type, translator in _qry_type_map.items()}

def py_to_qry_type(py_type: type) -> type:
	translator = _qry_type_map.get(py_type)
	if not translator:
		return py_type

	return translator.qry_type

def qry_to_py_type(qry_type: type) -> type:
	return _py_type_map.get(qry_type, qry_type)

def from_py(obj: Any) -> Any:
	if is_exported(type(obj)):
		return obj

	translator = _qry_type_map.get(type(obj))
	if not translator:
		raise QryRuntimeError(f'returning unsupported type ({type(obj)}) to qry: {obj}')

	return translator.translate_func(obj) # type: ignore

@dataclass
class Library:
	environment: Environment

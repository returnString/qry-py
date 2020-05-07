from typing import Any, List, Optional, cast
from types import ModuleType
from inspect import getmodule

_export_attr = '__qryexport__'
_original_module_attr = '__qrymodule__'

def export(obj: Any) -> Any:
	setattr(obj, _export_attr, True)
	return obj

def is_exported(obj: Any) -> bool:
	return hasattr(obj, _export_attr)

def set_original_module(obj: Any, source_module: Optional[ModuleType]) -> None:
	setattr(obj, _original_module_attr, source_module)

def get_original_module(obj: Any) -> Optional[ModuleType]:
	return cast(ModuleType, getattr(obj, _original_module_attr, getmodule(obj)))

def get_all_exported_objs(module: ModuleType) -> List[Any]:
	objects = []
	for name in dir(module):
		obj = getattr(module, name)
		original_obj_module = get_original_module(obj)

		if is_exported(obj) and original_obj_module and original_obj_module.__name__.startswith(module.__name__):
			objects.append(obj)

	return objects

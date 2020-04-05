from typing import Any, List
from types import ModuleType

_export_attr = '__qryexport__'

def export(obj: Any) -> Any:
	setattr(obj, _export_attr, True)
	return obj

def is_exported(obj: Any) -> bool:
	return hasattr(obj, _export_attr)

def get_all_exported_objs(module: ModuleType) -> List[Any]:
	ret = []
	for name in dir(module):
		obj = getattr(module, name)
		if is_exported(obj):
			ret.append(obj)
	return ret

from typing import Any

from qry.stdlib.core import String, Int
from qry.stdlib.export import export
from qry.runtime import method

@export
def my_mul_func(arg1: int, arg2: int) -> int:
	return arg1 * arg2

@export
@method
def str_or_int_method(obj: Any) -> Any:
	return NotImplemented

@str_or_int_method
def str_or_int_method_str(obj: String) -> Any:
	return True

@str_or_int_method
def str_or_int_method_int(obj: Int) -> Any:
	return False

@export
@method
def str_or_fallback_method(obj: Any) -> Any:
	return 'fallback'

@str_or_fallback_method
def str_or_fallback_method_str(obj: String) -> Any:
	return obj

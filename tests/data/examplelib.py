from typing import Any

from qry.common import export
from qry.lang import String, Int
from qry.runtime import method, TypeParam

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

@export
@method
def generic_dispatch(t: TypeParam) -> Any:
	return getattr(t, '__name__')

@generic_dispatch.generic(Int)
def generic_dispatch_int() -> Any:
	return 'special int'

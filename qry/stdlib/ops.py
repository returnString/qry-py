from typing import Any, Callable
import operator
import builtins

from .core import String, Int, Float, Bool
from .export import export
from ..environment import Environment
from ..runtime import method, from_py, FunctionBase, Function, BuiltinFunction, Method, Library, TypeParam

@method
def add(a: Any, b: Any) -> Any:
	pass

@method
def subtract(a: Any, b: Any) -> Any:
	pass

@method
def divide(a: Any, b: Any) -> Any:
	pass

@method
def multiply(a: Any, b: Any) -> Any:
	pass

@method
def equal(a: Any, b: Any) -> Any:
	pass

@method
def not_equal(a: Any, b: Any) -> Any:
	pass

@method
def greater_than(a: Any, b: Any) -> Any:
	pass

@method
def greater_than_or_equal(a: Any, b: Any) -> Any:
	pass

@method
def less_than(a: Any, b: Any) -> Any:
	pass

@method
def less_than_or_equal(a: Any, b: Any) -> Any:
	pass

@method
def negate_logical(a: Any) -> Any:
	pass

@method
def negate_arithmetic(a: Any) -> Any:
	pass

@add
def string_concat(a: String, b: String) -> String:
	return String(a.val + b.val)

def binop(a_type: type, b_type: type, op: Callable[[Any, Any], Any]) -> Any:
	def impl(a: a_type, b: b_type) -> Any: # type: ignore
		return from_py(op(a.val, b.val)) # type: ignore

	return impl

def unop(a_type: type, op: Callable[[Any], Any]) -> Any:
	def impl(a: a_type) -> Any: # type: ignore
		return from_py(op(a.val)) # type: ignore

	return impl

def numeric_binop_impl(a_type: type, b_type: type) -> None:
	add(binop(a_type, b_type, operator.add))
	subtract(binop(a_type, b_type, operator.sub))
	divide(binop(a_type, b_type, operator.truediv))
	multiply(binop(a_type, b_type, operator.mul))
	equal(binop(a_type, b_type, operator.eq))
	not_equal(binop(a_type, b_type, operator.ne))
	greater_than(binop(a_type, b_type, operator.gt))
	greater_than_or_equal(binop(a_type, b_type, operator.ge))
	less_than(binop(a_type, b_type, operator.lt))
	less_than_or_equal(binop(a_type, b_type, operator.le))

def numeric_unop_impl(a_type: type) -> None:
	negate_arithmetic(unop(a_type, operator.neg))

numeric_binop_impl(Int, Int)
numeric_binop_impl(Float, Float)
numeric_binop_impl(Int, Float)
numeric_binop_impl(Float, Int)
numeric_unop_impl(Int)
numeric_unop_impl(Float)

negate_logical(unop(Bool, operator.not_))
equal(binop(Bool, Bool, operator.eq))
not_equal(binop(Bool, Bool, operator.ne))

@export
@method
def to_string(obj: Any) -> str:
	pass

@export
@method
def print(obj: Any) -> None:
	builtins.print(to_string.call(obj, default = ''))

@to_string
def int_to_string(obj: Int) -> str:
	return str(obj.val)

@to_string
def float_to_string(obj: Float) -> str:
	return str(obj.val)

@to_string
def string_to_string(obj: String) -> str:
	return obj.val

@to_string
def bool_to_string(obj: Bool) -> str:
	return str(obj.val).lower()

def func_str(obj: FunctionBase) -> str:
	args = [f'{a.name}: {a.type}' for a in obj.args]
	return f'fn({", ".join(args)})'

@to_string
def func_to_string(obj: Function) -> str:
	return func_str(obj)

@to_string
def builtin_to_string(obj: BuiltinFunction) -> str:
	return func_str(obj)

@to_string
def method_to_string(obj: Method) -> str:
	options = ','.join(obj.funcs.keys())
	return f'fn(...): {options}'

def environment_to_string(obj: Environment) -> str:
	parent = obj.parent.name if obj.parent else 'none'
	return f'{obj.name} (parent: {parent}, entries: {len(obj.state)})'

@to_string
def library_to_string(obj: Library) -> str:
	return environment_to_string(obj.environment)

@export
@method
def num_cols(obj: Any) -> int:
	pass

@export
@method
def num_rows(obj: Any) -> int:
	pass

@export
@method
def cast(target_type: TypeParam, obj: Any) -> Any:
	pass

@cast.generic(Int)
def float_to_int(obj: Float) -> int:
	return int(obj.val)

@cast.generic(Float)
def int_to_float(obj: Int) -> float:
	return float(obj.val)

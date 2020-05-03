from typing import Any, Callable
import operator
from decimal import Decimal
import builtins

from .core import String, Number, Bool
from .export import export
from ..environment import Environment
from ..runtime import method, from_py, FunctionBase, Function, BuiltinFunction, Method, Library

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

def binop(target: type, op: Callable[[Any, Any], Any]) -> Any:
	def impl(a: target, b: target) -> Any: # type: ignore
		return from_py(op(a.val, b.val)) # type: ignore

	return impl

def unop(target: type, op: Callable[[Any], Any]) -> Any:
	def impl(a: target) -> Any: # type: ignore
		return from_py(op(a.val)) # type: ignore

	return impl

add(binop(Number, operator.add))
subtract(binop(Number, operator.sub))
divide(binop(Number, operator.truediv))
multiply(binop(Number, operator.mul))
equal(binop(Number, operator.eq))
not_equal(binop(Number, operator.ne))
greater_than(binop(Number, operator.gt))
greater_than_or_equal(binop(Number, operator.ge))
less_than(binop(Number, operator.lt))
less_than_or_equal(binop(Number, operator.le))
negate_arithmetic(unop(Number, operator.neg))

negate_logical(unop(Bool, operator.not_))
equal(binop(Bool, operator.eq))
not_equal(binop(Bool, operator.ne))

@export
@method
def to_string(obj: Any) -> str:
	pass

@export
@method
def print(obj: Any) -> None:
	builtins.print(to_string.call(obj, default = ''))

@to_string
def num_to_string(obj: Number) -> str:
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
	return 'fn(...)'

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

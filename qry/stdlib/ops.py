from typing import Any, Callable
import operator
from decimal import Decimal

from .core import String, Number, Bool
from .export import export
from ..runtime import method, from_py

@export
@method
def add(a: Any, b: Any) -> Any:
	pass

@export
@method
def subtract(a: Any, b: Any) -> Any:
	pass

@export
@method
def divide(a: Any, b: Any) -> Any:
	pass

@export
@method
def multiply(a: Any, b: Any) -> Any:
	pass

@export
@method
def equal(a: Any, b: Any) -> Any:
	pass

@export
@method
def not_equal(a: Any, b: Any) -> Any:
	pass

@export
@method
def greater_than(a: Any, b: Any) -> Any:
	pass

@export
@method
def greater_than_or_equal(a: Any, b: Any) -> Any:
	pass

@export
@method
def less_than(a: Any, b: Any) -> Any:
	pass

@export
@method
def less_than_or_equal(a: Any, b: Any) -> Any:
	pass

@export
@method
def negate_logical(a: Any) -> Any:
	pass

@export
@method
def negate_arithmetic(a: Any) -> Any:
	pass

@add
def string_concat(a: String, b: String) -> String:
	return String(a.val + b.val)

def binop(target: type, op: Callable[[Any, Any], Any]) -> Any:
	def impl(a: target, b: target) -> Any: # type: ignore
		return op(a.val, b.val) # type: ignore

	return impl

def unop(target: type, op: Callable[[Any], Any]) -> Any:
	def impl(a: target) -> Any: # type: ignore
		return op(a.val) # type: ignore

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

@to_string
def num_to_string(obj: Number) -> str:
	return str(obj.val)

@to_string
def string_to_string(obj: String) -> str:
	return obj.val

@to_string
def bool_to_string(obj: String) -> str:
	return str(obj.val)

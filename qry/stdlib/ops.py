from typing import Any, Callable
import operator
import builtins

from qry.lang import String, Int, Float, Bool, BinaryOp, UnaryOp
from qry.common import export
from qry.runtime import method, from_py, FunctionBase, Function, BuiltinFunction, Method, Library, TypeParam, Environment

@method
def add(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def subtract(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def divide(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def multiply(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def equal(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def not_equal(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def greater_than(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def greater_than_or_equal(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def less_than(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def less_than_or_equal(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def negate_logical(a: Any) -> Any:
	return NotImplemented

@method
def negate_arithmetic(a: Any) -> Any:
	return NotImplemented

@method
def and_(a: Any, b: Any) -> Any:
	return NotImplemented

@method
def or_(a: Any, b: Any) -> Any:
	return NotImplemented

@add
def string_concat(a: String, b: String) -> String:
	return String(a.val + b.val)

def binop(a_type: type, b_type: type, return_type: type, op: Callable[[Any, Any], Any]) -> Any:
	def impl(a: a_type, b: b_type) -> return_type: # type: ignore
		return from_py(op(a.val, b.val)) # type: ignore

	return impl

def unop(a_type: type, return_type: type, op: Callable[[Any], Any]) -> Any:
	def impl(a: a_type) -> return_type: # type: ignore
		return from_py(op(a.val)) # type: ignore

	return impl

def numeric_binop_impl(a_type: type, b_type: type, return_type: type) -> None:
	add(binop(a_type, b_type, return_type, operator.add))
	subtract(binop(a_type, b_type, return_type, operator.sub))
	divide(binop(a_type, b_type, return_type, operator.truediv))
	multiply(binop(a_type, b_type, return_type, operator.mul))
	equal(binop(a_type, b_type, Bool, operator.eq))
	not_equal(binop(a_type, b_type, Bool, operator.ne))
	greater_than(binop(a_type, b_type, Bool, operator.gt))
	greater_than_or_equal(binop(a_type, b_type, Bool, operator.ge))
	less_than(binop(a_type, b_type, Bool, operator.lt))
	less_than_or_equal(binop(a_type, b_type, Bool, operator.le))

def numeric_unop_impl(a_type: type) -> None:
	negate_arithmetic(unop(a_type, a_type, operator.neg))

numeric_binop_impl(Int, Int, Int)
numeric_binop_impl(Float, Float, Float)
numeric_binop_impl(Int, Float, Float)
numeric_binop_impl(Float, Int, Float)
numeric_unop_impl(Int)
numeric_unop_impl(Float)

negate_logical(unop(Bool, Bool, operator.not_))
equal(binop(Bool, Bool, Bool, operator.eq))
not_equal(binop(Bool, Bool, Bool, operator.ne))
and_(binop(Bool, Bool, Bool, operator.and_))
or_(binop(Bool, Bool, Bool, operator.or_))

@export
@method
def to_string(obj: Any) -> str:
	return f'<object: {type(obj).__name__}>'

@export
@method
def print(obj: Any) -> None:
	builtins.print(to_string.call([obj]))

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
	options = '\n'.join([f'{obj.name}({k})' for k in obj.funcs.keys()])
	return f'method {obj.name}(...) with specialisations:\n{options}'

def environment_to_string(obj: Environment) -> str:
	chain = ' -> '.join([e.name for e in obj.chain()])
	entries = '\n'.join([f'- ({type(v).__name__}) {k}' for k, v in obj.state.items()])
	return f'{obj.name} (chain: {chain}):\n{entries}'

@to_string
def library_to_string(obj: Library) -> str:
	return environment_to_string(obj.environment)

@export
@method
def num_cols(obj: Any) -> Any:
	return NotImplemented

@export
@method
def num_rows(obj: Any) -> Any:
	return NotImplemented

@export
@method
def cast(target_type: TypeParam, obj: Any) -> Any:
	return NotImplemented

@cast.generic(Int)
def float_to_int(obj: Float) -> int:
	return int(obj.val)

@cast.generic(Float)
def int_to_float(obj: Int) -> float:
	return float(obj.val)

binop_lookup = {
	BinaryOp.ADD: add,
	BinaryOp.SUBTRACT: subtract,
	BinaryOp.DIVIDE: divide,
	BinaryOp.MULTIPLY: multiply,
	BinaryOp.EQUAL: equal,
	BinaryOp.NOT_EQUAL: not_equal,
	BinaryOp.GREATER_THAN: greater_than,
	BinaryOp.GREATER_THAN_OR_EQUAL: greater_than_or_equal,
	BinaryOp.LESS_THAN: less_than,
	BinaryOp.LESS_THAN_OR_EQUAL: less_than_or_equal,
	BinaryOp.AND: and_,
	BinaryOp.OR: or_,
}

unop_lookup = {
	UnaryOp.NEGATE_LOGICAL: negate_logical,
	UnaryOp.NEGATE_ARITH: negate_arithmetic,
}

from typing import List, Any, Dict, Callable, Optional
from dataclasses import dataclass, field
import inspect
from enum import Enum, auto
from decimal import Decimal

from .syntax import Expr, FuncExpr
from .environment import Environment
from .stdlib.core import String, Number, Bool, Null
from .stdlib.export import is_exported

class ArgumentMode(Enum):
	STANDARD = auto()
	VARARGS = auto()
	KWARGS = auto()

@dataclass
class Argument:
	name: str
	type: Any
	eval_immediate: bool
	mode: ArgumentMode
	convert_to_py: bool

	def __repr__(self) -> str:
		return f'{self.name}: {self.type}'

@dataclass
class FunctionBase:
	args: List[Argument]

	def __repr__(self) -> str:
		return f'fn({", ".join([ repr(a) for a in self.args ])})'

@dataclass
class Function(FunctionBase):
	body: List[Expr]
	environment: Environment

_builtin_arg_types_to_convert = {
	str,
	bool,
	int,
	float,
	Decimal,
}

def _py_arg(arg_spec: inspect.FullArgSpec, name: str) -> Argument:
	annotated_type = arg_spec.annotations[name]
	if arg_spec.varargs == name:
		mode = ArgumentMode.VARARGS
	elif arg_spec.varkw == name:
		mode = ArgumentMode.KWARGS
	else:
		mode = ArgumentMode.STANDARD

	return Argument(name, annotated_type, annotated_type is not Expr, mode,
		annotated_type in _builtin_arg_types_to_convert)

def to_py(obj: Any) -> Any:
	if isinstance(obj, (String, Number, Bool)):
		return obj.val
	elif isinstance(obj, Null):
		return None

	return obj

def from_py(obj: Any) -> Any:
	if is_exported(type(obj)):
		return obj
	elif isinstance(obj, bool):
		return Bool(obj)
	if isinstance(obj, (int, float, Decimal)):
		return Number(obj)
	elif isinstance(obj, str):
		return String(obj)
	elif obj is None:
		return Null

	raise Exception(f'returning unsupported type ({type(obj)}) to qry: {obj}')

@dataclass
class BuiltinFunction(FunctionBase):
	func: Callable[..., Any]
	implicit_caller_env: bool

	def __repr__(self) -> str:
		return '[builtin] ' + super().__repr__()

	@classmethod
	def from_func(cls, func: Callable[..., Any]) -> 'BuiltinFunction':
		arg_spec = inspect.getfullargspec(func)
		arg_names = arg_spec.args
		if arg_spec.varargs:
			arg_names.append(arg_spec.varargs)
		if arg_spec.varkw:
			arg_names.append(arg_spec.varkw)

		implicit_caller_env = len(arg_names) > 0 and arg_names[0] == '_env'
		if implicit_caller_env:
			arg_names = arg_names[1:]

		args = [_py_arg(arg_spec, a) for a in arg_names]
		return cls(args, func, implicit_caller_env)

@dataclass
class Library:
	environment: Environment

	def __repr__(self) -> str:
		return f'library "{self.environment.name}" (object count: {len(self.environment.state)})'

def _method_sig(types: List[type]) -> str:
	return '|'.join([t.__name__ for t in types])

@dataclass
class Method:
	default_func: BuiltinFunction
	funcs: Dict[str, BuiltinFunction] = field(default_factory = dict)

	def __call__(self, impl_func: Callable[..., Any]) -> None:
		func_obj = BuiltinFunction.from_func(impl_func)
		args = [a.type for a in func_obj.args]
		self.funcs[_method_sig(args)] = func_obj

	def _resolve(self, types: List[type]) -> BuiltinFunction:
		return self.funcs.get(_method_sig(types), self.default_func)

	_no_default = object()

	def call(self, *args: Any, default: Any = _no_default) -> Any:
		func = self._resolve([type(a) for a in args])
		if func.func == _unimplemented and default != self._no_default:
			return default

		return func.func(*args)

_empty_func = lambda: None

def _unimplemented(*args: Any, **kwargs: Any) -> None:
	raise Exception(f'not implemented')

def method(ref_func: Callable[..., Any]) -> Method:
	ref_func = ref_func if ref_func.__code__.co_code != _empty_func.__code__.co_code else _unimplemented
	meth = Method(BuiltinFunction.from_func(ref_func))
	setattr(meth, '__name__', ref_func.__name__)
	return meth

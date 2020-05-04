from typing import List, Any, Dict, Callable, Optional
from dataclasses import dataclass, field
import inspect
from enum import Enum, auto

from .syntax import Expr, FuncExpr
from .environment import Environment
from .stdlib.core import String, Float, Int, Bool, Null
from .stdlib.export import is_exported

class QryRuntimeError(Exception):
	pass

class TypeParam:
	pass

class ArgumentMode(Enum):
	STANDARD = auto()
	VARARGS = auto()
	KWARGS = auto()
	TYPEPARAM = auto()

@dataclass
class Argument:
	name: str
	type: Any
	eval_immediate: bool
	mode: ArgumentMode
	convert_to_py: bool

@dataclass
class FunctionBase:
	args: List[Argument]

@dataclass
class Function(FunctionBase):
	body: List[Expr]
	environment: Environment

_builtin_arg_types_to_convert = {
	str,
	bool,
	int,
	float,
}

def _py_arg(arg_spec: inspect.FullArgSpec, name: str) -> Argument:
	annotated_type = arg_spec.annotations[name]
	if arg_spec.varargs == name:
		mode = ArgumentMode.VARARGS
	elif arg_spec.varkw == name:
		mode = ArgumentMode.KWARGS
	elif annotated_type == TypeParam:
		mode = ArgumentMode.TYPEPARAM
	else:
		mode = ArgumentMode.STANDARD

	return Argument(name, annotated_type, annotated_type is not Expr, mode,
		annotated_type in _builtin_arg_types_to_convert)

def to_py(obj: Any) -> Any:
	if isinstance(obj, (String, Int, Float, Bool)):
		return obj.val
	elif isinstance(obj, Null):
		return None

	return obj

def from_py(obj: Any) -> Any:
	if is_exported(type(obj)):
		return obj
	elif isinstance(obj, bool):
		return Bool(obj)
	if isinstance(obj, int):
		return Int(obj)
	if isinstance(obj, float):
		return Float(obj)
	elif isinstance(obj, str):
		return String(obj)
	elif obj is None:
		return Null()

	raise QryRuntimeError(f'returning unsupported type ({type(obj)}) to qry: {obj}')

@dataclass
class BuiltinFunction(FunctionBase):
	func: Callable[..., Any]
	implicit_caller_env: bool

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

def _method_sig(types: List[type]) -> str:
	return '|'.join([t.__name__ for t in types])

@dataclass
class Method:
	default_func: BuiltinFunction
	funcs: Dict[str, BuiltinFunction] = field(default_factory = dict)

	def _register(self, impl_func: Callable[..., Any], *types: type) -> Callable[..., Any]:
		func_obj = BuiltinFunction.from_func(impl_func)
		args = list(types) + [a.type for a in func_obj.args]
		self.funcs[_method_sig(args)] = func_obj
		return impl_func

	def __call__(self, impl_func: Callable[..., Any]) -> Callable[..., Any]:
		return self._register(impl_func)

	def generic(self, *types: type) -> Callable[..., Any]:
		def wrapper(impl_func: Callable[..., Any]) -> Callable[..., Any]:
			return self._register(impl_func, *types)

		return wrapper

	_no_default = object()

	def call(self, *args: Any, type_params: List[type] = [], default: Any = _no_default) -> Any:
		sig = _method_sig((type_params + [type(a) for a in args]))
		func = self.funcs.get(sig, self.default_func)
		ret = func.func(*args)
		if ret == NotImplemented:
			if default != self._no_default:
				return default
			raise QryRuntimeError(f'unimplemented method "{func.func.__name__}" for signature: {sig}')

		return ret

def method(ref_func: Callable[..., Any]) -> Method:
	meth = Method(BuiltinFunction.from_func(ref_func))
	setattr(meth, '__name__', ref_func.__name__)
	return meth

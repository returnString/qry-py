from typing import List, Any, Dict, Callable, Tuple
from dataclasses import dataclass, field
from inspect import getmodule

from qry.common import set_original_module

from .runtime import py_to_qry_type
from .function import BuiltinFunction
from .error import QryRuntimeError

def _method_sig(types: List[type]) -> str:
	if Any in types:
		raise QryRuntimeError(f'tried to create a method signature including {Any}')

	return '|'.join([t.__name__ for t in types])

@dataclass
class Method:
	name: str
	default_func: BuiltinFunction
	funcs: Dict[str, BuiltinFunction] = field(default_factory = dict)

	def _register(self, impl_func: Callable[..., Any], type_params: List[type]) -> Callable[..., Any]:
		func_obj = BuiltinFunction.from_func(impl_func)
		args = type_params + [a.type for a in func_obj.args]
		self.funcs[_method_sig(args)] = func_obj
		return impl_func

	def __call__(self, impl_func: Callable[..., Any]) -> Callable[..., Any]:
		return self._register(impl_func, [])

	def generic(self, *type_params: type) -> Callable[..., Any]:
		def wrapper(impl_func: Callable[..., Any]) -> Callable[..., Any]:
			return self._register(impl_func, list(type_params))

		return wrapper

	def resolve(
		self,
		arg_types: List[type],
		type_params: List[type] = [],
		allow_default: bool = True,
	) -> Tuple[str, BuiltinFunction]:
		sig = _method_sig(type_params + [py_to_qry_type(a) for a in arg_types])
		func = self.funcs.get(sig, self.default_func)

		if not allow_default and func == self.default_func:
			raise QryRuntimeError('default func disallowed')

		return sig, func

	def call(self, args: List[Any], type_params: List[type] = []) -> Any:
		sig, func = self.resolve([type(a) for a in args], type_params)

		# supply unhandled types as actual args for fallback generic dispatch
		if func == self.default_func and len(type_params):
			ret = func.func(*(type_params + args))
		else:
			ret = func.func(*args)

		if ret == NotImplemented:
			raise QryRuntimeError(f'unimplemented method "{func.func.__name__}" for signature: {sig}')

		return ret

def method(ref_func: Callable[..., Any]) -> Method:
	meth = Method(ref_func.__name__, BuiltinFunction.from_func(ref_func))
	setattr(meth, '__name__', ref_func.__name__)
	set_original_module(meth, getmodule(ref_func))
	return meth

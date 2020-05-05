from typing import List, Any, Callable
from dataclasses import dataclass, field
import inspect
from enum import Enum, auto

from qry.lang import Expr

from .environment import Environment

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

import builtins

from .core import Number
from .export import export

@export
def min(a: Number, b: Number) -> Number:
	return builtins.min(a, b)

@export
def max(a: Number, b: Number) -> Number:
	return builtins.max(a, b)

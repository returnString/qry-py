import builtins
from decimal import Decimal

from .export import export
from ..runtime import method

@export
def min(a: Decimal, b: Decimal) -> Decimal:
	return builtins.min(a, b)

@export
def max(a: Decimal, b: Decimal) -> Decimal:
	return builtins.max(a, b)

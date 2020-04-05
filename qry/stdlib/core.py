import builtins
from decimal import Decimal

from .export import export

@export
class Number(Decimal):
	pass

@export
class String(str):
	pass

@export
def print(*text: String) -> None:
	builtins.print(*text)

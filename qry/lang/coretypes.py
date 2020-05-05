from dataclasses import dataclass

from qry.common import export

@export
@dataclass
class Int:
	val: int

@export
@dataclass
class Float:
	val: float

@export
@dataclass
class String:
	val: str

@export
@dataclass
class Bool:
	val: bool

@export
class Null:
	pass

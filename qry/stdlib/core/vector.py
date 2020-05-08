from typing import Any, Iterable, Dict, cast
from dataclasses import dataclass

from qry.common import export
from qry.lang import Int, Float
from qry.runtime import method, TypeParam

from qry.stdlib.ops import length

from pyarrow import Array, Int64Array, FloatingPointArray, array

@export
@dataclass
class IntVector:
	data: Int64Array

@export
@dataclass
class FloatVector:
	data: FloatingPointArray

def _array_from_primitives(values: Iterable[Any]) -> Array:
	return array([v.val for v in values])

# TODO: improve method dispatch so we can have one vec method that accepts all types
@export
def intvec(*values: Int) -> IntVector:
	return IntVector(_array_from_primitives(values))

@export
def floatvec(*values: Float) -> FloatVector:
	return FloatVector(_array_from_primitives(values))

@export
@method
def sum(vec: Any) -> Any:
	return NotImplemented

@sum
def intvec_sum(vec: IntVector) -> int:
	return cast(int, vec.data.sum().as_py())

@sum
def floatvec_sum(vec: FloatVector) -> float:
	return float(vec.data.sum().as_py())

@length
def intvec_len(vec: IntVector) -> int:
	return len(vec.data)

@length
def floatvec_len(vec: FloatVector) -> int:
	return len(vec.data)

scalar_to_vector_lookup: Dict[type, type] = {
	Int: IntVector,
	Float: FloatVector,
}

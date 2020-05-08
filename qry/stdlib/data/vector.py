from typing import Any, Iterable, Dict, cast
from dataclasses import dataclass

from qry.common import export
from qry.lang import Int, Float
from qry.runtime import method, TypeParam

from qry.stdlib.ops import length

from pyarrow import Array, Int64Array, FloatingPointArray, array, int64, float64

@export
@dataclass
class Vector:
	data: Array

@export
class IntVector(Vector):
	pass

@export
class FloatVector(Vector):
	pass

def _array_from_primitives(values: Iterable[Any]) -> Array:
	return array([v.val for v in values])

_arrow_to_qry_types = {
	int64(): IntVector,
	float64(): FloatVector,
}

def vector_from_array(arr: Array) -> Vector:
	vec_type = _arrow_to_qry_types[arr.type]
	return vec_type(arr)

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

@export
@method
def mean(vec: Any) -> Any:
	return NotImplemented

@sum
def intvec_sum(vec: IntVector) -> int:
	return cast(int, vec.data.sum().as_py())

@mean
def intvec_mean(vec: IntVector) -> float:
	return int(vec.data.sum().as_py()) / len(vec.data)

@sum
def floatvec_sum(vec: FloatVector) -> float:
	return float(vec.data.sum().as_py())

@mean
def floatvec_mean(vec: FloatVector) -> float:
	return float(vec.data.sum().as_py()) / len(vec.data)

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

from dataclasses import dataclass
from typing import cast
from functools import reduce

from pyarrow import Table, csv, array
from numpy import concatenate

from qry.common import export
from qry.stdlib.ops import to_string, num_cols, num_rows

from .vector import Vector, vector_from_array

@export
@dataclass
class DataFrame:
	table: Table

@export
def read_csv(file: str) -> DataFrame:
	table = csv.read_csv(file)
	return DataFrame(table)

@to_string
def df_to_string(df: DataFrame) -> str:
	return str(df.table.to_pydict())

@num_cols
def df_num_cols(df: DataFrame) -> int:
	return len(df.table.columns)

@num_rows
def df_num_rows(df: DataFrame) -> int:
	return cast(int, df.table.num_rows)

@export
def col(df: DataFrame, name: str) -> Vector:
	# tables use chunked arrays, we want contiguous for vectors
	# this is awful, maybe scrap table usage altogether and convert asap for csv etc
	arr = [arr.to_numpy() for arr in df.table.column(name).chunks]
	return vector_from_array(array(reduce(concatenate, arr)))

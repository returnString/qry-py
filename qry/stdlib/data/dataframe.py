from dataclasses import dataclass
from typing import cast

import pyarrow
from pyarrow import csv

from qry.common import export
from qry.stdlib.ops import to_string, num_cols, num_rows

@export
@dataclass
class DataFrame:
	table: pyarrow.Table

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

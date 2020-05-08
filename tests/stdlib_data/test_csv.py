from ..eval_helpers import data_driven_test

test_csv = data_driven_test([
	('data.read_csv("tests/data/sql_bootstrap.csv") |> num_rows()', 3),
	('data.read_csv("tests/data/sql_bootstrap.csv") |> num_cols()', 2),
])

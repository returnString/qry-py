from ..eval_helpers import data_driven_test

csv_exprs = [
	('data.read_csv("tests/data/sql_bootstrap.csv") |> num_rows()', 3),
	('data.read_csv("tests/data/sql_bootstrap.csv") |> num_cols()', 2),
]

test_csv = data_driven_test(csv_exprs)

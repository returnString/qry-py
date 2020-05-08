from ..eval_helpers import data_driven_test

sql_bootstrap_csv = 'tests/stdlib_data/data/sql_bootstrap.csv'

test_csv = data_driven_test([
	(f'read_csv("{sql_bootstrap_csv}") |> num_rows()', 3),
	(f'read_csv("{sql_bootstrap_csv}") |> num_cols()', 2),
	(f'read_csv("{sql_bootstrap_csv}") |> col("age") |> sum()', 26 + 27 + 27),
],
	libs = ['data'])

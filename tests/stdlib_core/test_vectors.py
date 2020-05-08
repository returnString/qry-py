from ..eval_helpers import data_driven_test

vector_tests = [
	('intvec(1, 2, 3, 4) |> length()', 4),
	('floatvec(0, 0) |> length()', 2),
	('intvec(1, 2, 3) |> sum()', 6),
	('floatvec(1.5, 1.5, 3.5) |> sum()', 6.5),
]

test_vectors = data_driven_test(vector_tests)

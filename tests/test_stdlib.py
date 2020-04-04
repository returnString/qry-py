from .eval_helpers import data_driven_test

math_exprs = [
	('math.min(0, 1)', 0),
	('math.max(0, 1)', 1),
]

test_math_lib = data_driven_test(math_exprs)

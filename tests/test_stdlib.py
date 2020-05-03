from .eval_helpers import data_driven_test

math_exprs = [
	('math.min(0, 1)', 0),
	('math.max(0, 1)', 1),
]

test_math_lib = data_driven_test(math_exprs)

meta_exprs = [
	('meta.eval_ast(meta.get_ast(1 + 1))', 2),
	('''
	x <- 1
	meta.eval_ast(meta.get_ast(1 + 1 + x))''', 3),
]

test_meta_lib = data_driven_test(meta_exprs)

op_exprs = [
	('to_string(true)', 'true'),
	('to_string(1 + 1)', '2'),
	('to_string("some string")', 'some string'),
]

test_op_lib = data_driven_test(op_exprs)

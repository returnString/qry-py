from ..eval_helpers import data_driven_test

test_meta_lib = data_driven_test([
	('meta.eval_ast(meta.get_ast(1 + 1))', 2),
	('''
	x <- 1
	meta.eval_ast(meta.get_ast(1 + 1 + x))''', 3),
])

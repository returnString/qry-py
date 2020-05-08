from ..eval_helpers import data_driven_test

expressions_with_results = [
	('''
	add <- fn(x: Int, y: Int) {
		x + y
	}

	add(1, 2)
	''', 3),
	('''
	fixed_bonus <- 100
	add_with_closure <- fn(x: Int, y: Int) {
		x + y + fixed_bonus
	}

	add_with_closure(1, 2)
	''', 103),
	('''
	fn named_add(x: Int, y: Int) {
		x + y
	}

	named_add(1, 2)
	''', 3),
]

test_functions = data_driven_test(expressions_with_results)

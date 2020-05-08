from ..eval_helpers import data_driven_test

test_op_lib = data_driven_test([
	('1 + 2', 3),
	('1 + 2 * 3', 7),
	('(1 + 2) * 3', 9),
	('!true', False),
	('!false', True),
	('0 > 1', False),
	('0 < 1', True),
	('0 >= 1', False),
	('0 <= 1', True),
	(
	'''
		x <- 1
		y <- 2
		z <- x + y
		z == 3
		z == x
		z == y
		''',
	[1, 2, 3, True, False, False],
	),
	('"ohai" + ", " + "world"', "ohai, world"),
	('print("hi there")', None),
	('to_string(true)', 'true'),
	('to_string(1 + 1)', '2'),
	('to_string("some string")', 'some string'),
	('cast(Int, 2.5)', 2),
])

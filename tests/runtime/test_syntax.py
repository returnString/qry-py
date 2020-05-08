from qry.runtime import QryRuntimeError
from ..eval_helpers import data_driven_test

test_syntax = data_driven_test([
	('0', 0),
	('"hello there"', 'hello there'),
	('1.0', 1.0),
	('true', True),
	('false', False),
	('-1', -1),
	('null', None),
	('{{1}}', 1),
	('{{1 + 2 * 10}}', 21),
	('x', QryRuntimeError('not found: x')),
	('''
	x <- y <- z <- 0
	x + y + z
	''', 0),
	('''
	1 -> x -> y -> z
	x + y + z
	''', 3),
])

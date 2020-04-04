from typing import Any, List, Tuple, Dict

import pytest

from qry import Parser, Interpreter, Null

expressions_with_results = [
	('0', 0),
	('"hello there"', 'hello there'),
	('1 + 2', 3),
	('1 + 2 * 3', 7),
	('(1 + 2) * 3', 9),
	('1.0', 1.0),
	('true', True),
	('false', False),
	('!true', False),
	('!false', True),
	('-1', -1),
	('null', Null()),
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
]

expressions_with_final_state = [
	('''
	x <- y <- z <- 0
	''', {
	'x': 0,
	'y': 0,
	'z': 0,
	}),
	('''
	1 -> x -> y -> z
	''', {
	'x': 1,
	'y': 1,
	'z': 1,
	}),
	('''
	add <- fn(x, y) {
		x + y
	}

	x <- add(1, 2)
	''', {
	'x': 3
	}),
	('''
	fixed_bonus <- 100
	add_with_closure <- fn(x, y) {
		x + y + fixed_bonus
	}

	x <- add_with_closure(1, 2)
	''', {
	'x': 103
	}),
]

parser = Parser()

def _eval(source: str) -> Tuple[Interpreter, List[Any]]:
	interpreter = Interpreter()
	ast = parser.parse(source)
	return interpreter, [interpreter.eval(e) for e in ast]

@pytest.mark.parametrize("source, expected_result", expressions_with_results)
def test_expression_results(source: str, expected_result: Any) -> None:
	if not isinstance(expected_result, list):
		expected_result = [expected_result]

	_, results = _eval(source)
	result_types = [type(r) for r in results]
	expected_types = [type(r) for r in expected_result]

	assert result_types == expected_types
	assert results == expected_result

@pytest.mark.parametrize("source, expected_state", expressions_with_final_state)
def test_expression_state(source: str, expected_state: Dict[str, Any]) -> None:
	interpreter, _ = _eval(source)
	for k, expected_value in expected_state.items():
		assert k in interpreter.global_env.state
		value = interpreter.global_env.state[k]
		assert type(value) == type(expected_value)
		assert value == expected_value

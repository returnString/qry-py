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

	state_types = {k: type(v) for k, v in interpreter.state.items()}
	expected_types = {k: type(v) for k, v in expected_state.items()}

	assert state_types == expected_types
	assert interpreter.state == expected_state

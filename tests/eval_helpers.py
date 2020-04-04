from typing import Any, List, Tuple

import pytest

from qry import Parser, Interpreter

parser = Parser()

def eval(source: str, interpreter: Interpreter = Interpreter()) -> List[Any]:
	ast = parser.parse(source)
	return [interpreter.eval(e) for e in ast]

def eval_single(source: str, interpreter: Interpreter = Interpreter()) -> Any:
	results = eval(source, interpreter)
	assert len(results) == 1
	return results[0]

def data_driven_test(data: List[Tuple[str, Any]]) -> Any:
	@pytest.mark.parametrize("source, expected_result", data)
	def testwrapper(source: str, expected_result: Any) -> None:
		if not isinstance(expected_result, list):
			expected_result = [expected_result]

		results = eval(source)
		result_types = [type(r) for r in results]
		expected_types = [type(r) for r in expected_result]

		assert result_types == expected_types
		assert results == expected_result

	return testwrapper

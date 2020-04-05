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
		results = eval(source)
		if isinstance(expected_result, list):
			assert results == expected_result
		else:
			assert results[-1] == expected_result

	return testwrapper

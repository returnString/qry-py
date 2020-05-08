from typing import Any, List, Tuple, Optional, Callable

import pytest

from qry.lang import Parser
from qry.interpreter import Interpreter
from qry.runtime import to_py, QryRuntimeError

parser = Parser()

def eval(source: str, interpreter: Optional[Interpreter] = None) -> List[Any]:
	interpreter = interpreter or Interpreter()
	ast = parser.parse(source)
	return [to_py(interpreter.eval(e)) for e in ast]

def eval_single(source: str, interpreter: Optional[Interpreter] = None) -> Any:
	results = eval(source, interpreter)
	assert len(results) == 1
	return results[0]

def data_driven_test(data: List[Tuple[str, Any]],
	init_interpreter: Optional[Callable[[Interpreter], None]] = None) -> Any:
	@pytest.mark.parametrize("source, expected_result", data)
	def testwrapper(source: str, expected_result: Any) -> None:
		interpreter = Interpreter()

		if init_interpreter:
			init_interpreter(interpreter)

		if isinstance(expected_result, QryRuntimeError):
			with pytest.raises(type(expected_result), match = str(expected_result)):
				eval(source, interpreter)
		else:
			results = eval(source, interpreter)
			if isinstance(expected_result, list):
				assert results == expected_result
			else:
				assert results[-1] == expected_result

	return testwrapper

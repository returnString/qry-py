from typing import Any, List, Tuple, Optional, Callable

import pytest

from qry.lang import Parser
from qry.interpreter import Interpreter
from qry.runtime import to_py, QryRuntimeError

parser = Parser()

def data_driven_test(
	data: List[Tuple[str, Any]],
	*,
	libs: List[str] = [],
	init: Optional[Callable[[Interpreter], None]] = None,
) -> Any:
	@pytest.mark.parametrize("source, expected_result", data)
	def testwrapper(source: str, expected_result: Any) -> None:
		interpreter = Interpreter()

		def eval(source: str) -> List[Any]:
			ast = parser.parse(source)
			return [to_py(interpreter.eval(e)) for e in ast]

		if init:
			init(interpreter)

		for lib in libs:
			eval(f'attach({lib})')

		if isinstance(expected_result, QryRuntimeError):
			with pytest.raises(type(expected_result), match = str(expected_result)):
				eval(source)
		else:
			results = eval(source)
			if isinstance(expected_result, list):
				assert results == expected_result
			else:
				assert results[-1] == expected_result

	return testwrapper

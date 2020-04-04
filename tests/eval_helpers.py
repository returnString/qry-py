from typing import Any, List
from qry import Parser, Interpreter

parser = Parser()

def eval(source: str, interpreter: Interpreter = Interpreter()) -> List[Any]:
	ast = parser.parse(source)
	return [interpreter.eval(e) for e in ast]

def eval_single(source: str, interpreter: Interpreter = Interpreter()) -> Any:
	results = eval(source, interpreter)
	assert len(results) == 1
	return results[0]

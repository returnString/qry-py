from glob import glob
from pathlib import Path

import pytest

from qry.lang import Parser
from qry.interpreter import Interpreter

@pytest.mark.parametrize("filename", glob('tests/code/**/*.qry', recursive = True))
def test_code_files(filename: str) -> None:
	code = Path(filename).read_text()
	parser = Parser()
	interpreter = Interpreter()
	for expr in parser.parse(code):
		interpreter.eval(expr)

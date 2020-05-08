#!/usr/bin/env python

from cmd import Cmd
import sys
from pathlib import Path

from qry.lang import Parser
from qry.interpreter import Interpreter
from qry.runtime import QryRuntimeError
from qry.stdlib.ops import print as print_method

parser = Parser()
interpreter = Interpreter()

class QryCmd(Cmd):
	prompt = 'qry> '

	def default(self, line: str) -> bool:
		try:
			for expr in parser.parse(line):
				val = interpreter.eval(expr)
				print(f'({type(val).__name__}) ', end = '')
				print_method.call([val])
		except QryRuntimeError as err:
			print(err)

		return False

args = sys.argv[1:]
if len(args) == 0:
	cmd = QryCmd()
	cmd.cmdloop()
else:
	script_file = Path(args[0]).read_text()
	for expr in parser.parse(script_file):
		interpreter.eval(expr)

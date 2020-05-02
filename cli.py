from cmd import Cmd

from qry import Parser, Interpreter, InterpreterError
from qry.stdlib.ops import to_string

parser = Parser()
interpreter = Interpreter()

class QryCmd(Cmd):
	prompt = 'qry> '

	def default(self, line: str) -> bool:
		try:
			for expr in parser.parse(line):
				val = interpreter.eval(expr)
				string_func = to_string.try_resolve([type(val)])
				str_val = string_func.func(val) if string_func else ''
				print(f'({type(val).__name__}) {str_val}')
		except InterpreterError as err:
			print(err)

		return False

cmd = QryCmd()
cmd.cmdloop()

from cmd import Cmd

from qry import Parser, Interpreter, InterpreterError

parser = Parser()
interpreter = Interpreter()

class QryCmd(Cmd):
	prompt = 'qry> '

	def default(self, line: str) -> bool:
		try:
			for expr in parser.parse(line):
				val = interpreter.eval(expr)
				print(f'({type(val).__name__}) {val}')
		except InterpreterError as err:
			print(err)

		return False

cmd = QryCmd()
cmd.cmdloop()

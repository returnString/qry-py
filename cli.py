from cmd import Cmd

from qry import Parser, Interpreter

parser = Parser()
interpreter = Interpreter()

class QryCmd(Cmd):
	prompt = 'qry> '

	def default(self, line: str) -> bool:
		for expr in parser.parse(line):
			val = interpreter.eval(expr)
			print(repr(val))

		return False

cmd = QryCmd()
cmd.cmdloop()

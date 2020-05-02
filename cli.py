from cmd import Cmd
import builtins

from qry.parser import Parser
from qry.interpreter import Interpreter, InterpreterError
from qry.stdlib.ops import print

parser = Parser()
interpreter = Interpreter()

class QryCmd(Cmd):
	prompt = 'qry> '

	def default(self, line: str) -> bool:
		try:
			for expr in parser.parse(line):
				val = interpreter.eval(expr)
				builtins.print(f'({type(val).__name__}) ', end = '')
				print.call(val)
		except InterpreterError as err:
			builtins.print(err)

		return False

cmd = QryCmd()
cmd.cmdloop()

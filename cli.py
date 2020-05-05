from cmd import Cmd
import builtins

from qry.lang import Parser
from qry.interpreter import Interpreter
from qry.runtime import QryRuntimeError
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
				print.call([val])
		except QryRuntimeError as err:
			builtins.print(err)

		return False

cmd = QryCmd()
cmd.cmdloop()

from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from qry.lang import Expr

@dataclass
class Environment:
	name: str
	state: Dict[str, Any]
	interpreter_hooks: Any # TODO: move interpreter eval logic into runtime?
	parent: Optional['Environment'] = None

	def chain(self) -> List['Environment']:
		ret = []
		parent = self.parent
		while parent:
			ret.append(parent)
			parent = parent.parent
		return ret

	def child_env(self, name: str) -> 'Environment':
		child_state = self.state.copy()
		return Environment(name, child_state, self.interpreter_hooks, self)

	def eval(self, expr: Expr) -> Any:
		return self.interpreter_hooks.eval_in_env(expr, self)

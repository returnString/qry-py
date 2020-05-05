from typing import Any, Dict, Optional, List
from dataclasses import dataclass

@dataclass
class Environment:
	name: str
	state: Dict[str, Any]
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
		return Environment(name, child_state, self)

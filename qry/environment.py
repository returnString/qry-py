from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class Environment:
	name: str
	state: Dict[str, Any]

	def child_env(self, name: str) -> 'Environment':
		child_state = self.state.copy()
		return Environment(name, child_state)

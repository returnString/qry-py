from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class Environment:
	name: str
	state: Dict[str, Any]
	parent: Optional['Environment'] = None

	def child_env(self, name: str) -> 'Environment':
		child_state = self.state.copy()
		return Environment(name, child_state, self)

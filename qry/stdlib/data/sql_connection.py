from typing import Optional, Iterable, Any, Dict, Callable, Tuple
from typing_extensions import Protocol
from dataclasses import dataclass

from qry.common import export
from qry.lang import BinaryOp

class DBCursor(Protocol):
	def execute(self, sql: str, parameters: Iterable[Any] = ...) -> 'DBCursor':
		...

	def fetchall(self) -> Any:
		...

	description: Any
	rowcount: int

class DBConn(Protocol):
	def cursor(self, cursorClass: Optional[type] = ...) -> DBCursor:
		...

@dataclass
class ColumnMetadata:
	type: type

BinopRewrite = Optional[Tuple[ColumnMetadata, str]]

@export
@dataclass
class Connection:
	c: DBConn
	get_table_metadata: Callable[['Connection', str], Dict[str, ColumnMetadata]]
	rewrite_binop: Optional[Callable[[BinaryOp, ColumnMetadata, str, ColumnMetadata, str], BinopRewrite]] = None

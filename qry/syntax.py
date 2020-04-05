from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict

@dataclass
class SourceInfo:
	line: int

@dataclass # type: ignore
class Expr(ABC):
	source: SourceInfo

	@abstractmethod
	def render(self) -> str:
		pass

@dataclass
class AssignExpr(Expr):
	lhs: Expr
	rhs: Expr

	def render(self) -> str:
		return f'{self.lhs.render()} <- {self.rhs.render()}'

class BinaryOp(Enum):
	ADD = '+'
	SUBTRACT = '-'
	MULTIPLY = '*'
	DIVIDE = '/'

	EQUAL = '=='
	NOT_EQUAL = '!='
	GREATER_THAN = '>'
	GREATER_THAN_OR_EQUAL = '>='
	LESS_THAN = '<'
	LESS_THAN_OR_EQUAL = '<='

	ACCESS = '.'

	LASSIGN = '<-'
	RASSIGN = '->'

_binary_ops_without_spaces = {
	BinaryOp.ACCESS,
}

@dataclass
class BinaryOpExpr(Expr):
	lhs: Expr
	op: BinaryOp
	rhs: Expr

	def __post_init__(self) -> None:
		if self.op == BinaryOp.LASSIGN and not isinstance(self.lhs, IdentExpr):
			raise Exception('can only assign to idents')

	def render(self) -> str:
		op_spacing = '' if self.op in _binary_ops_without_spaces else ' '
		return f'({self.lhs.render()}{op_spacing}{self.op.value}{op_spacing}{self.rhs.render()})'

class UnaryOp(Enum):
	NEGATE_ARITH = '-'
	NEGATE_LOGICAL = '!'

@dataclass
class UnaryOpExpr(Expr):
	op: UnaryOp
	arg: Expr

	def render(self) -> str:
		return f'{self.op.value}{self.arg.render()}'

@dataclass
class StringLiteral(Expr):
	value: str

	def render(self) -> str:
		return f'"{self.value}"'

@dataclass
class IntLiteral(Expr):
	value: int

	def render(self) -> str:
		return str(self.value)

@dataclass
class FloatLiteral(Expr):
	value: float

	def render(self) -> str:
		return str(self.value)

@dataclass
class BoolLiteral(Expr):
	value: bool

	def render(self) -> str:
		return str(self.value)

@dataclass
class IdentExpr(Expr):
	value: str

	def render(self) -> str:
		return self.value

@dataclass
class NullLiteral(Expr):
	def render(self) -> str:
		return 'null'

@dataclass
class FuncExpr(Expr):
	args: Dict[str, Expr]
	body: List[Expr]

	def render(self) -> str:
		body = '\n'.join([e.render() for e in self.body])
		args = ', '.join([f'{k}: {v}' for k, v in self.args.items()])
		return f'fn({args}) {{ {body} }}'

@dataclass
class CallExpr(Expr):
	func: Expr
	args: List[Expr]

	def render(self) -> str:
		return f'{self.func.render()}({", ".join([ a.render() for a in self.args ])})'

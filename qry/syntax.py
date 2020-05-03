from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict

from .stdlib.core import Int, Float, String, Bool, Null

@dataclass
class SourceInfo:
	line: int

@dataclass # type: ignore
class Expr(ABC):
	source: SourceInfo

	@abstractmethod
	def render(self) -> str:
		pass

	def children(self) -> List['Expr']:
		return [e for e in self.__dict__.values() if isinstance(e, Expr)]

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

	PIPE = '|>'

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
	value: String

	def render(self) -> str:
		return f'"{self.value.val}"'

@dataclass
class IntLiteral(Expr):
	value: Int

	def render(self) -> str:
		return str(self.value.val)

@dataclass
class FloatLiteral(Expr):
	value: Float

	def render(self) -> str:
		return str(self.value.val)

@dataclass
class BoolLiteral(Expr):
	value: Bool

	def render(self) -> str:
		return str(self.value.val)

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
	positional_args: List[Expr]
	named_args: Dict[str, Expr]

	def render(self) -> str:
		named = [f'{name} = {a.render()}' for name, a in self.named_args.items()]
		positional = [a.render() for a in self.positional_args]
		args = ', '.join(positional + named)
		return f'{self.func.render()}({args})'

@dataclass
class InterpolateExpr(Expr):
	contents: Expr

	def render(self) -> str:
		return f'{{{{{self.contents.render()}}}}}'

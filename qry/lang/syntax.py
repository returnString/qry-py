from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union

from .coretypes import String, Int, Float, Bool

@dataclass
class SourceInfo:
	line: int

@dataclass # type: ignore
class Expr(ABC):
	source: SourceInfo

	@abstractmethod
	def render(self) -> str:
		pass

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

	ACCESS = '::'

	LASSIGN = '<-'
	RASSIGN = '->'

	PIPE = '|>'

	# TODO: short-circuiting variants
	AND = "&"
	OR = "|"

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
		return str(self.value.val).lower()

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
	name: Optional[str]
	args: Dict[str, Expr]
	return_type: Expr
	body: List[Expr]

	def render(self) -> str:
		body = ' '.join([e.render() for e in self.body])
		args = ', '.join([f'{k}: {v.render()}' for k, v in self.args.items()])
		name = f' {self.name}' if self.name else ''
		return f'fn{name}({args}) -> {self.return_type.render()} {{ {body} }}'

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

class UseWildcard:
	pass

@dataclass
class UseExpr(Expr):
	libs: List[str]
	imports: Union[UseWildcard, List[str]]

	def render(self) -> str:
		lib_path = '::'.join(self.libs)
		if isinstance(self.imports, UseWildcard):
			return f'use {lib_path}::*'

		if len(self.libs):
			imports = ', '.join(self.imports)
			return f'use {lib_path}::{{{imports}}}'

		chain = '::'.join(self.imports)
		return f'use {chain}'

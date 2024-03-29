from typing import Any, Callable, Type, List, Dict, cast
from pathlib import Path
import sys

from lark import Lark, Transformer, v_args

from .coretypes import String, Int, Float, Bool
from .syntax import *

def _passthrough() -> Any:
	return lambda self, children, meta: children

def _binop(right_associative: bool = False) -> Any:
	def binop(self: 'ASTBuilder', children: List[Any], meta: Any) -> BinaryOpExpr:
		source = self._source_info(meta)
		if right_associative:
			state = BinaryOpExpr(source, children[-3], BinaryOp(children[-2]), children[-1])
			for i in range(len(children) - 4, 0, -2):
				state = BinaryOpExpr(source, children[i - 1], BinaryOp(children[i]), state)
		else:
			state = BinaryOpExpr(source, children[0], BinaryOp(children[1]), children[2])
			for i in range(3, len(children), 2):
				state = BinaryOpExpr(source, state, BinaryOp(children[i]), children[i + 1])
		return state

	return binop

def _unop() -> Any:
	return lambda self, children, meta: UnaryOpExpr(self._source_info(meta), UnaryOp(children[0]), children[1])

def _literal(literal_class: type, func: Callable[[Any], Any]) -> Any:
	return lambda self, children, meta: literal_class(self._source_info(meta), func(children[0]))

@v_args(meta = True)
class ASTBuilder(Transformer): # type: ignore
	def _source_info(self, meta: Any) -> SourceInfo:
		return SourceInfo(meta.line)

	add_expr = _binop()
	mul_expr = _binop()
	compare_expr = _binop()
	access_expr = _binop()
	lassign_expr = _binop(right_associative = True)
	rassign_expr = _binop()
	pipe_expr = _binop()
	and_expr = _binop()
	or_expr = _binop()

	negate_expr = _unop()

	int_literal = _literal(IntLiteral, lambda x: Int(int(x)))
	float_literal = _literal(FloatLiteral, lambda x: Float(float(x)))
	string_literal = _literal(StringLiteral, lambda x: String(str(x)[1:-1]))

	def bool_literal_true(self, children: List[Any], meta: Any) -> BoolLiteral:
		return BoolLiteral(self._source_info(meta), Bool(True))

	def bool_literal_false(self, children: List[Any], meta: Any) -> BoolLiteral:
		return BoolLiteral(self._source_info(meta), Bool(False))

	def null_literal(self, children: List[Any], meta: Any) -> NullLiteral:
		return NullLiteral(self._source_info(meta))

	def ident_expr(self, children: List[Any], meta: Any) -> IdentExpr:
		return IdentExpr(self._source_info(meta), children[0].value)

	def args_def(self, children: List[Any], meta: Any) -> Dict[str, Expr]:
		return {arg.children[0]: arg.children[1] for arg in children}

	def func_expr(self, children: List[Any], meta: Any) -> FuncExpr:
		name = None
		child_offset = 0
		if len(children) == 4:
			child_offset = 1
			name = children[0]

		args = children[child_offset]
		return_type = children[child_offset + 1]
		body = children[child_offset + 2]

		return FuncExpr(self._source_info(meta), name, args, return_type, body)

	def call_expr(self, children: List[Any], meta: Any) -> Any:
		positional = []
		named = {}

		for child in children[1]:
			if isinstance(child, Expr):
				positional.append(child)
			else:
				name, expr = child
				named[name] = expr

		return CallExpr(self._source_info(meta), children[0], positional, named)

	def paren_expr(self, children: List[Any], meta: Any) -> Any:
		return children[0][0]

	def named_provided_arg(self, children: List[Any], meta: Any) -> Any:
		return (children[0].value, children[1])

	call_arglist = _passthrough()
	block_expr = _passthrough()

	def interpolate_expr(self, children: List[Any], meta: Any) -> Any:
		return InterpolateExpr(self._source_info(meta), children[0])

	def use_wildcard(self, children: List[Any], meta: Any) -> Any:
		return UseWildcard()

	def use_lib_chain(self, children: List[Any], meta: Any) -> Any:
		return [c.value for c in children]

	def use_list(self, children: List[Any], meta: Any) -> Any:
		return [c.value for c in children]

	def use_expr(self, children: List[Any], meta: Any) -> UseExpr:
		if len(children) == 1:
			last_lib = children[0][-1]
			children.append([last_lib])
			children[0] = children[0][:-1]

		return UseExpr(self._source_info(meta), children[0], children[1])

def _get_data_file(file: str) -> Path:
	try:
		base_path = Path(sys._MEIPASS) # type: ignore
	except AttributeError:
		base_path = Path('.').absolute()

	return base_path / Path(file)

lark_parser = Lark.open(
	_get_data_file('qry/lang/grammar.lark'),
	parser = 'lalr',
	propagate_positions = True,
	debug = True,
)

class Parser:
	_builder = ASTBuilder()

	def parse(self, text: str) -> List[Expr]:
		tree = lark_parser.parse(text)
		return cast(List[Expr], self._builder.transform(tree).children)

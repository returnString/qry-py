from ..eval_helpers import data_driven_test

test_syntax = data_driven_test([
	('to_string(get_ast(1 + 1 + 3))', '((1 + 1) + 3)'),
	('to_string(get_ast(!true))', '!true'),
	('to_string(get_ast(null))', 'null'),
	('to_string(get_ast(my_ident))', 'my_ident'),
	('to_string(get_ast("some_string"))', '"some_string"'),
	('to_string(get_ast(call_func(with_args, arg2)))', 'call_func(with_args, arg2)'),
	('to_string(get_ast(use mylib))', 'use mylib'),
	('to_string(get_ast(use mylib::*))', 'use mylib::*'),
	('to_string(get_ast(use mylib::{thing1, thing2}))', 'use mylib::{thing1, thing2}'),
	('to_string(get_ast(fn(x: Int, y: Int) -> Null { x + y }))', 'fn(x: Int, y: Int) -> Null { (x + y) }'),
	('to_string(get_ast(fn(x: Int, y: Int) -> Int { x + y }))', 'fn(x: Int, y: Int) -> Int { (x + y) }'),
	('to_string(get_ast({{some_interpolated_expr}}))', '{{some_interpolated_expr}}'),
],
	libs = ['meta'])

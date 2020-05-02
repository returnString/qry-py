from .eval_helpers import data_driven_test

math_exprs = [
	('math.min(0, 1)', 0),
	('math.max(0, 1)', 1),
]

test_math_lib = data_driven_test(math_exprs)

meta_exprs = [
	('meta.eval_ast(meta.get_ast(1 + 1))', 2),
	('''
	x <- 1
	meta.eval_ast(meta.get_ast(1 + 1 + x))''', 3),
]

test_meta_lib = data_driven_test(meta_exprs)

table_bootstrap = '''
attach(data)

conn <- connect_sqlite(":memory:")
execute(conn, "create table my_table (name text, age integer)")
execute(conn, "insert into my_table(name, age) values ('ruan', 26), ('ruanlater', 27), ('thirdperson', 27)")
'''

data_exprs = [
	(table_bootstrap + '''
	get_table(conn, "my_table")
		|> filter(age <= 26)
		|> count_rows()
	''', 1),
	(table_bootstrap + '''
	get_table(conn, "my_table")
		|> aggregate(group(age), total_years = sum(age))
		|> count_rows()
	''', 2),
	(table_bootstrap + '''
	get_table(conn, "my_table")
		|> cross_join(get_table(conn, "my_table"))
		|> count_rows()
	''', 9),
]

test_data_lib = data_driven_test(data_exprs)

op_exprs = [
	('to_string(true)', 'true'),
	('to_string(1 + 1)', '2'),
	('to_string("some string")', 'some string'),
]

test_op_lib = data_driven_test(op_exprs)

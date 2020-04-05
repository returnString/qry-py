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
conn <- data.connect_sqlite(":memory:")
data.execute(conn, "create table my_table (name text, age integer)")
data.execute(conn, "insert into my_table(name, age) values ('ruan', 26), ('ruanlater', 27), ('thirdperson', 27)")
'''

data_exprs = [
	(table_bootstrap + '''
	data.get_table(conn, "my_table")
		|> data.filter(age <= 26)
		|> data.count_rows()
	''', 1),
	(table_bootstrap + '''
	data.get_table(conn, "my_table")
		|> data.aggregate(age, sum(age))
		|> data.count_rows()
	''', 2),
]

test_data_lib = data_driven_test(data_exprs)

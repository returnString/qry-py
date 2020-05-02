from uuid import uuid4

from .eval_helpers import data_driven_test

connect = '''
attach(data)
conn <- connect_postgres("localhost", 54321, "qrytest", "qry", "password")
'''

run_id = str(uuid4()).replace('-', '')

def table_name(name: str) -> str:
	return f'qry_{run_id}_{name}'

postgres_exprs = [
	(connect + f'''
	execute(conn, "create table {table_name('my_table')} (name text, age integer)")
	execute(conn, "insert into {table_name('my_table')}(name, age) values ('ruan', 26), ('ruanlater', 27), ('thirdperson', 27)")
	''', None),
	(connect + f'''
	get_table(conn, "{table_name('my_table')}")
		|> filter(age <= 26)
		|> count_rows()
	''', 1),
	(connect + f'''
	get_table(conn, "{table_name('my_table')}")
		|> aggregate(group(age), total_years = sum(age))
		|> count_rows()
	''', 2),
	(connect + f'''
	get_table(conn, "{table_name('my_table')}")
		|> cross_join(get_table(conn, "{table_name('my_table')}"))
		|> count_rows()
	''', 9),
]

test_postgres = data_driven_test(postgres_exprs)

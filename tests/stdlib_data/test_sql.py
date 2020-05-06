from uuid import uuid4
import os
from typing import Any, List, Tuple, Optional

from qry.runtime import QryRuntimeError

from ..eval_helpers import data_driven_test

run_id = str(uuid4()).replace('-', '')

def table_name(name: str) -> str:
	return f'qry_{run_id}_{name}'

data_exprs = [
	(f'''
	execute(conn, "create table {table_name('my_table')} (name text, age integer)")
	execute(conn, "insert into {table_name('my_table')}(name, age) values ('ruan', 26), ('ruanlater', 27), ('thirdperson', 27)")
	''', 3),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> filter(age <= 26)
		|> collect()
		|> num_rows()
	''', 1),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> aggregate(group(age), total_years = sum(age))
		|> collect()
		|> num_rows()
	''', 2),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> cross_join(get_table(conn, "{table_name('my_table')}"))
		|> collect()
		|> num_rows()
	''', 9),
	(f'''
	max_age <- 26
	get_table(conn, "{table_name('my_table')}")
		|> filter(age <= {{{{max_age}}}})
		|> collect()
		|> num_rows()
	''', 1),
	(f'''
	max_age <- 26
	get_table(conn, "{table_name('my_table')}")
		|> filter(name != "ruan" && name != "ruanlater")
		|> collect()
		|> num_rows()
	''', 1),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> mutate(next_year = age + 1)
		|> filter(next_year == 27)
		|> collect()
		|> num_rows()
	''', 1),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> select(name)
		|> collect()
		|> num_cols()
	''', 1),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> select(name, age)
		|> collect()
		|> num_cols()
	''', 2),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> select(1 + 1)
		|> collect()
	''', QryRuntimeError('expected expr of type:')),
]

def data_test(connect_code: str) -> Any:
	tests = [('attach(data) ' + connect_code + code, expectation) for code, expectation in data_exprs]
	return data_driven_test(tests)

test_sqlite = data_test('conn <- connect_sqlite("tests/artefacts/db.sqlite")')

if not os.getenv('QRY_CI_NODOCKER'):
	test_postgres = data_test('conn <- connect_postgres("localhost", 54321, "qrytest", "qry", "password")')
	test_mysql = data_test('conn <- connect_mysql("127.0.0.1", 33060, "qrytest", "qry", "password")')

from uuid import uuid4
import os
from typing import Any, List, Tuple, Optional

from ..eval_helpers import data_driven_test

run_id = str(uuid4()).replace('-', '')

def table_name(name: str) -> str:
	return f'qry_{run_id}_{name}'

data_exprs = [
	(f'''
	execute(conn, "create table {table_name('my_table')} (name text, age integer)")
	execute(conn, "insert into {table_name('my_table')}(name, age) values ('ruan', 26), ('ruanlater', 27), ('thirdperson', 27)")
	''', None),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> filter(age <= 26)
		|> count_rows()
	''', 1),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> aggregate(group(age), total_years = sum(age))
		|> count_rows()
	''', 2),
	(f'''
	get_table(conn, "{table_name('my_table')}")
		|> cross_join(get_table(conn, "{table_name('my_table')}"))
		|> count_rows()
	''', 9),
]

def data_test(connect_code: str) -> Any:
	tests = [('attach(data) ' + connect_code + code, expectation) for code, expectation in data_exprs]
	return data_driven_test(tests)

test_sqlite = data_test('conn <- connect_sqlite("tests/artefacts/db.sqlite")')

if not os.getenv('QRY_CI_NODOCKER'):
	test_postgres = data_test('conn <- connect_postgres("localhost", 54321, "qrytest", "qry", "password")')

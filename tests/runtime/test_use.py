from qry.runtime import QryRuntimeError

from ..eval_helpers import data_driven_test

test_syntax = data_driven_test([
	(''' 
	use data
	data::intvec(1) |> data::sum()
	''', 1),
	('''
	data::intvec(1)
	''', QryRuntimeError('not found: data')),
	(''' 
	use data::*
	intvec(1) |> sum()
	''', 1),
	(''' 
	use data::{intvec}
	intvec(1) |> sum()
	''', QryRuntimeError('not found: sum')),
])

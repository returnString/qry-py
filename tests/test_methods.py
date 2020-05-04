from qry.interpreter import Interpreter
from qry.runtime import QryRuntimeError

from .eval_helpers import data_driven_test
from .data import examplelib

def init_interpreter(interpreter: Interpreter) -> None:
	interpreter.load_library(examplelib, True)

method_tests = [
	('str_or_int_method("test")', True),
	('str_or_int_method(1)', False),
	('str_or_int_method(1.0)', QryRuntimeError('unimplemented method "str_or_int_method" for signature: Float')),
	('str_or_fallback_method("test")', 'test'),
	('str_or_fallback_method(1)', 'fallback'),
	('str_or_fallback_method(null)', 'fallback'),
	('generic_dispatch(Int)', 'special int'),
	('generic_dispatch(Float)', 'Float'),
	('generic_dispatch(String)', 'String'),
]

test_methods = data_driven_test(method_tests, init_interpreter)

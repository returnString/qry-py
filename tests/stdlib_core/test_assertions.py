from qry.runtime import QryAssertionFailed

from ..eval_helpers import data_driven_test

assertion_tests = [
	('assert(false)', QryAssertionFailed('assertion failed: false')),
	('assert(1 + 1 == 3)', QryAssertionFailed('')),
	('assert(1 + 1 == 2)', None),
]

test_assertions = data_driven_test(assertion_tests)

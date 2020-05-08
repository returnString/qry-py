from qry.common import export_named
from qry.runtime import Environment, QryAssertionFailed
from qry.lang import Expr, Bool

@export_named('assert')
def assert_(_env: Environment, expr: Expr) -> None:
	ret = _env.eval(expr)
	if not isinstance(ret, Bool):
		raise QryAssertionFailed('assert requires a boolean expression')

	if not ret.val:
		raise QryAssertionFailed(f'assertion failed: {expr.render()}')

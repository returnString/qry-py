from decimal import Decimal

class Number(Decimal):
	pass

class String(str):
	pass

class CoreLib:
	Number = Number
	String = String

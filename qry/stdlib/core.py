from decimal import Decimal

class CoreLib:
	class Number(Decimal):
		pass

	class String(str):
		pass

	def print(self, text: String) -> None:
		print(text)

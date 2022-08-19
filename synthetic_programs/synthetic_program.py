from operator import add, mul, sub


def synthetic_program(
	X1: int,
	X2: int,
	X3: int,
):
	"""Causal structure:
		('X1', 'Y1')
		('X1', 'Y2')
		('X2', 'Y2')
		('X2', 'Y3')
		('X2', 'Y5')
		('Y5', 'Y7')
		('X3', 'Y4')
		('X3', 'Y6')
		('X3', 'Y7')
	"""
	Y5 = mul(X2, X2)
	Y1 = mul(-9, X1)
	Y2 = sub(mul(-7, -7), add(X1, X2))
	Y3 = mul(X2, -4)
	Y4 = add(X3, 10)
	Y6 = sub(X3, X3)
	Y7 = sub(add(X3, 10), add(Y5, Y5))
	return Y1, Y2, Y3, Y4, Y5, Y6, Y7

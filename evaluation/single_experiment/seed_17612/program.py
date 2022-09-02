def program(
	X1: int,
	X2: int,
	X3: int,
	X4: int,
	X5: int,
	X6: int,
	Y1: int = None,
	Y2: int = None,
	Y3: int = None,
	Y4: int = None,
):
	"""Causal structure:
		('X1', 'Y1')
		('X2', 'Y2')
		('X3', 'Y3')
		('X3', 'Y4')
		('Y3', 'Y4')
	"""
	if Y3 is None:
		Y3 = X3+X3
	if Y1 is None:
		Y1 = X1-1
	if Y2 is None:
		Y2 = -34*X2
	if Y4 is None:
		Y4 = Y3-X3
	return {'Y1': Y1, 'Y2': Y2, 'Y3': Y3, 'Y4': Y4}

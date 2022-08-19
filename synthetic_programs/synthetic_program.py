def synthetic_program(
	X1: int,
	X2: int,
):
	"""Causal structure:
		('X1', 'Y1')
		('X1', 'Y2')
		('X1', 'Y3')
		('X1', 'Y4')
		('X1', 'Y5')
		('X1', 'Y7')
		('Y1', 'Y5')
		('Y1', 'Y7')
		('Y2', 'Y3')
		('Y2', 'Y5')
		('Y3', 'Y4')
		('Y4', 'Y5')
		('Y5', 'Y6')
		('Y7', 'Y8')
	"""
	Y1 = X1*0
	Y2 = 9-X1
	Y3 = (Y2*8)-(8*X1)
	Y4 = (Y3*3)+(Y3*X1)
	Y5 = (((4-Y4)+(Y4-Y2))*((Y1+4)-(Y1*X1)))-(((Y2+4)*(X1+Y1))-((Y1-Y2)-(4+Y4)))
	Y7 = (Y1+X1)*(X1--2)
	Y6 = -7-Y5
	Y8 = Y7*Y7
	return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8


if __name__ == "__main__":
	outputs = synthetic_program(1, 2)
	print(outputs)
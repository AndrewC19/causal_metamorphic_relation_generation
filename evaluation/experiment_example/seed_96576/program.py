def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
	Y1: int = None,
	Y2: int = None,
	Y3: int = None,
	Y4: int = None,
	Y5: int = None,
	Y6: int = None,
	Y7: int = None,
	Y8: int = None,
	Y9: int = None,
	Y10: int = None,
	Y11: int = None,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y5')
    ('X1', 'Y6')
    ('X1', 'Y11')
    ('Y1', 'Y6')
    ('Y6', 'Y10')
    ('X2', 'Y1')
    ('X2', 'Y2')
    ('X2', 'Y4')
    ('Y2', 'Y7')
    ('Y4', 'Y11')
    ('X3', 'Y3')
    ('X3', 'Y7')
    ('X3', 'Y8')
    ('Y3', 'Y9')
    ('Y7', 'Y9')
    ('Y7', 'Y10')
    ('Y10', 'Y11')
    """
    if Y1 is None:
        Y1 = X1 * X2
    if Y2 is None:
        Y2 = 35 + X2
    if Y3 is None:
        Y3 = X3 - 8
    if Y4 is None:
        Y4 = X2 + -41
    if Y5 is None:
        Y5 = X1 + 3
    if Y6 is None:
        Y6 = Y1 + X1
    if Y7 is None:
        Y7 = X3 + Y2
    if Y8 is None:
        Y8 = -6 * X3
    if Y9 is None:
        Y9 = Y3 * Y7
    if Y10 is None:
        Y10 = Y6 + Y7
    if Y11 is None:
        Y11 = Y10 - (Y4 * X1)
    return {"Y1": Y1, "Y2": Y2, "Y3": Y3, "Y4": Y4, "Y5": Y5, "Y6": Y6, "Y7": Y7, "Y8": Y8, "Y9": Y9, "Y10": Y10, "Y11": Y11}

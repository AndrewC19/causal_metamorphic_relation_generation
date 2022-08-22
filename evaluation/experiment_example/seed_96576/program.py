def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
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
    Y1 = X1 * X2
    Y2 = 35 + X2
    Y3 = X3 - 8
    Y4 = X2 + -41
    Y6 = Y1 + X1
    Y7 = X3 + Y2
    Y10 = Y6 + Y7
    Y5 = X1 + 3
    Y8 = -6 * X3
    Y9 = Y3 * Y7
    Y11 = Y10 - (Y4 * X1)
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9, Y10, Y11

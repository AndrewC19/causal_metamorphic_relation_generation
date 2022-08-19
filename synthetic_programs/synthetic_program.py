def synthetic_program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    X6: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y3')
    ('X1', 'Y6')
    ('Y1', 'Y5')
    ('Y3', 'Y5')
    ('X2', 'Y3')
    ('X2', 'Y5')
    ('X2', 'Y7')
    ('Y5', 'Y9')
    ('X3', 'Y2')
    ('X3', 'Y3')
    ('X3', 'Y8')
    ('Y2', 'Y3')
    ('Y2', 'Y8')
    ('Y2', 'Y9')
    ('X4', 'Y3')
    ('X4', 'Y4')
    ('X4', 'Y5')
    ('X4', 'Y9')
    ('Y4', 'Y6')
    ('X5', 'Y5')
    ('X5', 'Y9')
    ('X6', 'Y3')
    """
    Y1 = -7 * X1
    Y2 = X3 + X3
    Y3 = X6 - (X2 * ((X3 + X4) * (Y2 + X1)))
    Y4 = X4 + -31
    Y5 = Y3 * ((X2 * X5) + (Y1 + X4))
    Y6 = X1 + Y4
    Y7 = 46 + X2
    Y8 = X3 * Y2
    Y9 = (X4 - (Y5 - X5)) + Y2
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9

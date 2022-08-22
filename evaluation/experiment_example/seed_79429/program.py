def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
):
    """Causal structure:
    ('X1', 'Y7')
    ('X1', 'Y9')
    ('X2', 'Y7')
    ('X3', 'Y1')
    ('X3', 'Y5')
    ('Y1', 'Y2')
    ('Y1', 'Y3')
    ('Y1', 'Y6')
    ('Y1', 'Y7')
    ('Y1', 'Y9')
    ('Y5', 'Y10')
    ('X4', 'Y5')
    ('X4', 'Y10')
    ('Y2', 'Y3')
    ('Y2', 'Y4')
    ('Y2', 'Y10')
    ('Y3', 'Y9')
    ('X5', 'Y2')
    ('X5', 'Y8')
    ('Y8', 'Y10')
    ('Y4', 'Y6')
    """
    Y1 = 17 - X3
    Y2 = Y1 * X5
    Y3 = Y1 * Y2
    Y4 = Y2 * Y2
    Y5 = X3 * X4
    Y8 = -22 * X5
    Y6 = Y1 + Y4
    Y7 = (Y1 + X1) - X2
    Y9 = Y1 * (Y3 - X1)
    Y10 = X4 - (Y8 - (Y2 + Y5))
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9, Y10

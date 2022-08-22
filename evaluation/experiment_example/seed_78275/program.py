def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    X6: int,
):
    """Causal structure:
    ('X1', 'Y8')
    ('X2', 'Y3')
    ('X2', 'Y7')
    ('Y3', 'Y5')
    ('Y7', 'Y8')
    ('X3', 'Y1')
    ('X3', 'Y9')
    ('Y1', 'Y2')
    ('Y1', 'Y5')
    ('Y1', 'Y6')
    ('Y1', 'Y9')
    ('X4', 'Y5')
    ('Y5', 'Y9')
    ('X5', 'Y2')
    ('X5', 'Y4')
    ('X5', 'Y6')
    ('Y2', 'Y3')
    ('Y2', 'Y9')
    ('X6', 'Y3')
    ('X6', 'Y9')
    """
    Y1 = -44 - X3
    Y2 = X5 - Y1
    Y3 = X2 - (X6 * Y2)
    Y5 = (X4 + Y3) - Y1
    Y7 = 32 * X2
    Y4 = -15 - X5
    Y6 = X5 * Y1
    Y8 = X1 - Y7
    Y9 = X3 - ((Y5 * Y1) - (X6 * Y2))
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9

def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    X6: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y8')
    ('Y1', 'Y8')
    ('X2', 'Y4')
    ('Y4', 'Y6')
    ('X3', 'Y3')
    ('X3', 'Y9')
    ('Y3', 'Y5')
    ('Y3', 'Y7')
    ('Y3', 'Y8')
    ('X4', 'Y7')
    ('X4', 'Y8')
    ('X5', 'Y2')
    ('Y2', 'Y3')
    ('Y2', 'Y9')
    ('Y5', 'Y9')
    ('Y6', 'Y7')
    ('Y6', 'Y9')
    """
    Y1 = X1 - X1
    Y2 = 26 + X5
    Y3 = Y2 + X3
    Y4 = -49 - X2
    Y5 = 31 + Y3
    Y6 = Y4 + -48
    Y7 = (Y3 + Y6) + X4
    Y8 = (X1 - Y1) * (Y3 + X4)
    Y9 = (Y6 - (X3 + Y2)) - Y5
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9

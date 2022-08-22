def seed_97430(
    X1: int,
    X2: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y4')
    ('X1', 'Y5')
    ('X1', 'Y8')
    ('Y1', 'Y2')
    ('Y1', 'Y3')
    ('Y1', 'Y7')
    ('Y4', 'Y5')
    ('Y4', 'Y6')
    ('Y4', 'Y7')
    ('Y2', 'Y8')
    ('Y3', 'Y5')
    ('Y3', 'Y7')
    """
    Y1 = X1 - 33
    Y2 = Y1 - -29
    Y3 = Y1 - 14
    Y4 = 39 - X1
    Y5 = (X1 - Y3) * Y4
    Y6 = 6 + Y4
    Y7 = Y1 * (Y3 + Y4)
    Y8 = Y2 * X1
    return Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8

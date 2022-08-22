def seed_43022(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y2')
    ('X1', 'Y3')
    ('Y1', 'Y4')
    ('Y3', 'Y5')
    ('X2', 'Y3')
    ('X2', 'Y5')
    ('X3', 'Y4')
    ('X4', 'Y5')
    ('X4', 'Y6')
    """
    Y1 = X1 - -40
    Y3 = X2 + X1
    Y2 = X1 - -28
    Y4 = Y1 + X3
    Y5 = (X2 + Y3) + X4
    Y6 = X4 * 44
    return Y1, Y2, Y3, Y4, Y5, Y6

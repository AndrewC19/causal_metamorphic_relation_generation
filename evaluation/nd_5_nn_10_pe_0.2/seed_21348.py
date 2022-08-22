def seed_21348(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y3')
    ('Y1', 'Y6')
    ('Y3', 'Y4')
    ('X2', 'Y2')
    ('X2', 'Y5')
    ('Y2', 'Y4')
    ('X3', 'Y4')
    ('X3', 'Y5')
    ('X3', 'Y6')
    """
    Y1 = -20 + X1
    Y2 = X2 * 22
    Y3 = X1 + X1
    Y4 = Y3 + (Y2 + X3)
    Y5 = X2 - X3
    Y6 = Y1 - X3
    return Y1, Y2, Y3, Y4, Y5, Y6

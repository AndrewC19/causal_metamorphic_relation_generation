def seed_3724(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
):
    """Causal structure:
    ('X1', 'Y1')
    ('X1', 'Y3')
    ('X1', 'Y4')
    ('Y1', 'Y4')
    ('Y3', 'Y4')
    ('Y3', 'Y5')
    ('Y4', 'Y5')
    ('X2', 'Y4')
    ('X3', 'Y2')
    ('X3', 'Y5')
    ('X4', 'Y2')
    ('X4', 'Y5')
    ('X5', 'Y3')
    """
    Y1 = X1 + -23
    Y3 = X5 - X1
    Y4 = X2 * ((X1 + Y3) * Y1)
    Y2 = X3 - X4
    Y5 = (Y3 * X3) * (Y4 - X4)
    return Y1, Y2, Y3, Y4, Y5

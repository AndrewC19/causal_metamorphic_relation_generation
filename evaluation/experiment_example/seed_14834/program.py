def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    Y1 : int,
    Y2 : int,
    Y3 : int,
    Y4 : int,
    Y5 : int,
    Y6 : int,
    Y7 : int,
    Y8 : int,
    Y9 : int,
    Y10: int,
):
    """Causal structure:
    ('X1', 'Y6')
    ('Y6', 'Y9')
    ('X2', 'Y1')
    ('X2', 'Y3')
    ('X2', 'Y7')
    ('X2', 'Y10')
    ('Y3', 'Y6')
    ('Y3', 'Y10')
    ('X3', 'Y6')
    ('X4', 'Y2')
    ('X4', 'Y4')
    ('X4', 'Y5')
    ('X4', 'Y6')
    ('X4', 'Y8')
    ('X4', 'Y10')
    ('Y4', 'Y7')
    ('X5', 'Y5')
    ('X5', 'Y6')
    ('X5', 'Y7')
    ('Y9', 'Y10')
    """
    Y3 = -27 + X2
    Y4 = 14 + X4
    Y6 = Y3 * ((X5 - X3) + (X1 + X4))
    Y9 = Y6 + Y6
    Y1 = X2 - X2
    Y2 = X4 * X4
    Y5 = X5 - X4
    Y7 = X5 * (X2 + Y4)
    Y8 = -22 + X4
    Y10 = X2 + (Y3 + (Y9 + X4))
    return {"Y1": Y1, "Y2": Y2, "Y3": Y3, "Y4": Y4, "Y5": Y5, "Y6": Y6, "Y7": Y7, "Y8": Y8, "Y9": Y9, "Y10": Y10}

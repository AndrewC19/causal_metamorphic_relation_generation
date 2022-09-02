def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    Y1 : int = None,
    Y2 : int = None,
    Y3 : int = None,
    Y4 : int = None,
    Y5 : int = None,
    Y6 : int = None,
    Y7 : int = None,
    Y8 : int = None,
    Y9 : int = None,
    Y10: int = None,
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
    if Y1 is None:
        Y1 = X2 - 2
    if Y2 is None:
        Y2 = X4 * X4
    if Y3 is None:
        Y3 = -27 + X2
    if Y4 is None:
        Y4 = 14 + X4
    if Y5 is None:
        Y5 = X5 - X4
    if Y6 is None:
        Y6 = Y3 * ((X5 - X3) + (X1 + X4))
    if Y7 is None:
        Y7 = X5 * (X2 + Y4)
    if Y8 is None:
        Y8 = -22 + X4
    if Y9 is None:
        Y9 = Y6 + Y6
    if Y10 is None:
        Y10 = X2 + (Y3 + (Y9 + X4))
    return {"Y1": Y1, "Y2": Y2, "Y3": Y3, "Y4": Y4, "Y5": Y5, "Y6": Y6, "Y7": Y7, "Y8": Y8, "Y9": Y9, "Y10": Y10}

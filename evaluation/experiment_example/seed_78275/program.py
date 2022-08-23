def program(
    X1: int,
    X2: int,
    X3: int,
    X4: int,
    X5: int,
    X6: int,
    Y1 : int = None,
    Y2 : int = None,
    Y3 : int = None,
    Y4 : int = None,
    Y5 : int = None,
    Y6 : int = None,
    Y7 : int = None,
    Y8 : int = None,
    Y9 : int = None,
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
    if Y1 is None:
        Y1 = -44 - X3
    if Y2 is None:
        Y2 = X5 - Y1
    if Y3 is None:
        Y3 = X2 - (X6 * Y2)
    if Y4 is None:
        Y4 = -15 - X5
    if Y5 is None:
        Y5 = (X4 + Y3) - Y1
    if Y6 is None:
        Y6 = X5 * Y1
    if Y7 is None:
        Y7 = 32 * X2
    if Y8 is None:
        Y8 = X1 - Y7
    if Y9 is None:
        Y9 = X3 - ((Y5 * Y1) - (X6 * Y2))
    return {"Y1": Y1, "Y2": Y2, "Y3": Y3, "Y4": Y4, "Y5": Y5, "Y6": Y6, "Y7": Y7, "Y8": Y8, "Y9": Y9}

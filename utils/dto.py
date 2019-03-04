class CookieAmount(object):
    def __init__(self, amount, cps):
        self.amount = amount
        self.cps = cps


class Product(object):
    def __init__(self, cost, cps, element):
        self.cost = cost
        self.cps = cps
        self.element = element

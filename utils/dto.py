class CookieAmount(object):
    def __init__(self, amount, cps):
        self.amount = amount
        self.cps = cps


class Product(object):
    def __init__(self, cost, cps, element):
        self.cost = cost
        self.cps = cps
        self.element = element


class Building(object):
    def __init__(self, name, cost, cps, element):
        self.name = name
        self.cost = cost
        self.cps = cps
        self.element = element


class Upgrade(object):
    def __init__(self, upgrade_type, cost, element):
        self.upgrade_type = upgrade_type
        self.cost = cost
        self.cps = None
        self.element = element

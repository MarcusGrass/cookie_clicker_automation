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


class HourlyReport(object):
    def __init__(self, balance, cps, heaveny_chips):
        self.balance = balance
        self.cps = cps
        self.heavenly_chips = heaveny_chips

        self.delta_balance = None
        self.delta_cps = None
        self.delta_hc = None

        self.balance_increase = None
        self.cps_increase = None
        self.hc_increase = None

    def calculate_hourly_report_stats(self, new_balance, new_cps, new_heavenly_chips):
        self.delta_balance = new_balance - self.balance
        self.delta_cps = new_cps - self.cps
        self.delta_hc = new_heavenly_chips - self.heavenly_chips

        self.balance_increase = (new_balance/self.balance - 1)*100
        self.cps_increase = (new_cps/self.cps - 1)*100
        self.hc_increase = (new_heavenly_chips/self.heavenly_chips - 1)*100

        self.balance = new_balance
        self.cps = new_cps
        self.heavenly_chips = new_heavenly_chips

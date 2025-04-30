# player.py
class Player:
    def __init__(self, name):
        self.name = name
        self.units = []
        self.cp = 0

    def add_unit(self, unit):
        self.units.append(unit)

    def remove_dead(self):
        self.units = [u for u in self.units if u.is_alive()]

    def has_units(self):
        return any(u.is_alive() for u in self.units)

    def gain_cp(self, amount=1):
        self.cp += amount

    def spend_cp(self, cost):
        if self.cp >= cost:
            self.cp -= cost
            return True
        return False
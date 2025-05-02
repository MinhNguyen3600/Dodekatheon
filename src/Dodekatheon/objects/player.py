# player.py
class Player:
    def __init__(self, name):
        self.name = name
        self.units = []
        self.cp = 0
        self.vp     = 0      

    def gain_cp(self, n):
        self.cp += n

    def add_unit(self, unit):
        self.units.append(unit)

    def remove_dead(self):
        self.units = [u for u in self.units if u.is_alive()]

    def has_units(self):
        return any(u.is_alive() for u in self.units)
    
    def total_damage(self):
        return sum(u.stats['damage_dealt'] for u in self.units)

    def total_models_killed(self):
        return sum(u.stats['models_killed'] for u in self.units)

    def total_ranged_hit_pct(self):
        att = sum(u.stats['ranged_attacks'] for u in self.units)
        hit = sum(u.stats['ranged_hits']    for u in self.units)
        return (hit/att*100) if att>0 else 0

    def total_melee_hit_pct(self):
        att = sum(u.stats['melee_attacks'] for u in self.units)
        hit = sum(u.stats['melee_hits']    for u in self.units)
        return (hit/att*100) if att>0 else 0

    def gain_cp(self, amount=1):
        self.cp += amount

    def spend_cp(self, cost):
        if self.cp >= cost:
            self.cp -= cost
            return True
        return False
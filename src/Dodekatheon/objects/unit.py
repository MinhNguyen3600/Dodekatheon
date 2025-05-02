# unit.py
from objects.dice import roll_d6, roll_d3
import math

class Unit:
    _id_counter = 1

    def __init__(self, name, symbol, x, y, datasheet):
        self.id = Unit._id_counter
        Unit._id_counter += 1
        self.name = name
        self.symbol = symbol
        
        self.position = (x, y)
        self.datasheet = datasheet

        # squad size (1 for characters, >1 for multi-model units)
        self.size = datasheet.get('size', 1)

        # wounds per individual model
        self.wounds_per_model = datasheet['W']

        # total pooled wounds for the squad
        self.max_wounds = self.size * self.wounds_per_model
        self.current_wounds = self.max_wounds

        self.advanced = False
        self.fell_back = False
        self.charged = False
        self.battle_shocked = False
        # instead of one datasheet-wide loadout, make a list per model:
        self.models = [ {'wargear': None} for _ in range(self.size) ]
        # attachments holds other Unit instances (Characters)
        self.attachments = []

        self.stats = {
            'rng_fired':       0,
            'rng_hits':        0,
            'melee_fired':     0,
            'melee_hits':      0,
            'mortal_wounds':   0,
            'damage_dealt':    0,
            'models_killed':   0,
            'cp_spent':        0
        }

    def register_damage_dealt(self, *, dmg, models_killed, is_ranged, is_melee, mortal_wounds=0):
        # update damage and kills
        self.stats['damage_dealt']  += dmg + mortal_wounds
        self.stats['models_killed'] += models_killed
        if is_ranged:
            self.stats['ranged_attacks'] += getattr(self, '_last_num_attacks', 0)
            self.stats['ranged_hits']    += getattr(self, '_last_hits', 0)
        if is_melee:
            self.stats['melee_attacks'] += getattr(self, '_last_num_attacks', 0)
            self.stats['melee_hits']    += getattr(self, '_last_hits', 0)
        # clear last for next round
        self._last_num_attacks = self._last_hits = None

    @property
    def current_models(self):
        return math.ceil(self.current_wounds/self.wounds_per_model)

    def attach_leader(self, leader_unit):
        if leader_unit.name in self.datasheet['attachable_leaders']:
            self.attachments.append(leader_unit)
            # increase size & wounds
            self.size += leader_unit.size
            self.max_wounds += leader_unit.max_wounds
            self.current_wounds += leader_unit.current_wounds

    def choose_wargear(self):
        """Console-UI: let user swap wargear pre-game."""
        opts = self.datasheet['wargear_options']
        if not opts:
            return
        for wg_name, choices in opts.items():
            print(f"For weapon {wg_name} you may choose:")
            for i,ch in enumerate(choices):
                print(f"  {i}: replace with {ch['replace_with']}")
            pick = input("Pick option or ENTER to keep default: ")
            if pick.isdigit():
                choice = choices[int(pick)]
                # record choice on one of your models:
                self.models[0]['wargear']=choice['replace_with']

    def is_alive(self):
        return self.current_wounds > 0
    
    @property
    def below_half_strength(self):
        import math
        # characters (size=1): wounds < half their W characteristic
        if self.size == 1:
            # e.g. W=3 → half=1.5 → ceil(1.5)=2 → below if current_wounds<2
            return self.current_wounds < math.ceil(self.wounds_per_model/2)
        # multi-model: models remaining < half starting models
        return self.current_models < math.ceil(self.size/2)

    def take_damage(self, d=1):
        # subtract from pooled wounds
        self.current_wounds = max(0, self.current_wounds - d)

    @property
    def current_models(self):
        # how many individual models remain (round up)
        return math.ceil(self.current_wounds / self.wounds_per_model)
    
    @property
    def below_half_strength(self):
        # Characters (size==1): below half if wounds < half of wounds_per_model
        if self.size == 1:
            return self.current_wounds < (self.wounds_per_model / 2)
        # Multi-model: below half if remaining models < half of starting size
        return self.current_models < (self.size / 2)

    def display_stats(self):
        ds = self.datasheet
        print(
            f"{self.name} (ID {self.id}) - Pos:{self.position} "
            f"Wounds:{self.current_wounds}/{self.max_wounds} "
            f"Models:{self.current_models}/{self.size} "
            f"M:{ds['M']} T:{ds['T']} Sv:{ds['Sv']} W:{ds['W']}"
        )

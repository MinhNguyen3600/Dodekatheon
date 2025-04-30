# datasheet_loader.py
import json
from data.weapon_abilities import WeaponAbility
from data.unit_abilities import LoneOperative, DarkAngelsBodyguard

def build_weapon(entry, kind):
    """
    entry: list describing one weapon
      - ranged:  [ name, range, A, BS, S, AP, D, [abil_list] ]
      - melee:   [ name, A, WS, S, AP, D, [abil_list] ]
    kind: 'ranged' or 'melee'
    """
    # unpack common tail (optional abilities list)
    *base, maybe_abils = entry
    if isinstance(maybe_abils, list):
        core = base
        abil_keys = maybe_abils
    else:
        core = entry
        abil_keys = []

    if kind == 'ranged':
        name, rng, A, Skill, S, AP, D = core
        # parse range
        if isinstance(rng, str) and rng.endswith('"'):
            rng_val = int(rng.rstrip('"'))
        else:
            rng_val = int(rng)
        BS = int(str(Skill).rstrip('+'))
        weapon = {
            'name': name,
            'range': rng_val,
            'A': A,
            'BS': BS,
            'S': S,
            'AP': AP,
            'D': D,
            'type': 'ranged',
            'abilities': WeaponAbility(abil_keys)
        }
    else:
        # melee
        name, A, Skill, S, AP, D = core
        WS = int(str(Skill).rstrip('+'))
        weapon = {
            'name': name,
            'range': None,
            'A': A,
            'WS': WS,
            'S': S,
            'AP': AP,
            'D': D,
            'type': 'melee',
            'abilities': WeaponAbility(abil_keys)
        }

    return weapon

def build_unit_ability(name, cfg):
    t = cfg['type']
    if t == 'dark_angels_bodyguard':
        return DarkAngelsBodyguard(radius=cfg.get('radius',3))
    if t == 'lone_operative':
        return LoneOperative(max_range=cfg.get('max_range',12))
    # … other unit-level abilities …
    return None

class DatasheetLoader:
    def __init__(self, path='data/datasheets.json'):
        with open(path) as f:
            self.data = json.load(f)

    def get_unit(self, key):
        entry = self.data[key]
        M, T, Sv_raw, W, Ld_raw, OC_raw = entry['statline']

        # parse and convert saves, leadership, objective control to ints
        Sv = int(str(Sv_raw).rstrip('+'))
        Ld = int(str(Ld_raw).rstrip('+'))
        OC = int(str(OC_raw).rstrip('+'))

        ranged = [ build_weapon(w, 'ranged') for w in entry.get('ranged_weapons', []) ]
        melee  = [ build_weapon(w, 'melee')  for w in entry.get('melee_weapons', []) ]
        unit_abilities = []
        for nm, cfg in entry.get('abilities',{}).items():
            abil = build_unit_ability(nm, cfg)
            if abil:
                unit_abilities.append(abil)
        return {
            # carry through the number-of-models field
            'size': entry.get('size', 1),
            'M': M,
            'T': T,
            'Sv': Sv,
            'W': W,
            'Ld': int(str(Ld).rstrip('+')),
            'OC': int(str(OC).rstrip('+')),
            'ranged_weapons': ranged,
            'melee_weapons': melee,
            'unit_abilities': unit_abilities,
            'specialRules': entry.get('specialRules',{})
        }

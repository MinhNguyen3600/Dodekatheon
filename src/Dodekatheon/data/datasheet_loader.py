# data/datasheet_loader.py
import json
from data.weapon_abilities import WeaponAbility
from data.unit_abilities import *

def build_weapon(entry, kind):
    # unchanged from your existing function…
    *base, maybe_abils = entry
    if isinstance(maybe_abils, list):
        core, abil_keys = base, maybe_abils
    else:
        core, abil_keys = entry, []
    if kind == 'ranged':
        name, rng, A, Skill, S, AP, D = core

        rng_val = int(rng.rstrip('"')) if isinstance(rng,str) else int(rng)
        try:
            BS = int(str(Skill).rstrip('+'))
        except ValueError:
            BS = None  # For auto-hit weapons like Flamers

        return {
            'name': name,
            'range': rng_val,
            'A': A, 'BS': BS, 'S': S, 'AP': AP, 'D': D,
            'type': 'ranged',
            'abilities': WeaponAbility(abil_keys)
        }
    
    else:
        name, A, Skill, S, AP, D = core

        WS = None if str(Skill).upper() == "N/A" else int(str(Skill).rstrip('+'))
        
        return {
            'name': name,
            'range': None,
            'A': A, 'WS': WS, 'S': S, 'AP': AP, 'D': D,
            'type': 'melee',
            'abilities': WeaponAbility(abil_keys)
        }

def build_weapon_group(entry, kind):
    """
    Supports two formats:
      1) Legacy single-profile: entry is a list [ name, … , [abils] ]
      2) New grouping form: entry is { "name":…, "profiles":[ [ … ], … ] }
    """
    # legacy single-profile format?
    if isinstance(entry, list):
        w = build_weapon(entry, kind)
        return { 'name': w['name'], 'profiles': [ w ] }

    # new dict format
    wg = {'name': entry['name'], 'profiles': []}
    for prof in entry.get('profiles', []):
        wg['profiles'].append(build_weapon(prof, kind))
    return wg

def build_unit_ability(name, cfg):
    t = cfg['type']
    if t == 'deep_strike':
        return DeepStrike()
    if t == 'dark_angels_bodyguard':
        return DarkAngelsBodyguard(radius=cfg.get('radius',3))
    if t == 'lone_operative':
        return LoneOperative(max_range=cfg.get('max_range',12))
    if t == 'leader':
        return Leader()
    if t == 'master_of_the_stances':
        return MasterOfTheStances(cfg.get('once_per'))
    if t == 'strategic_mastery':
        return StrategicMastery(cfg.get('once_per'))
    if t == 'resolute_will':
        return ResoluteWill()
    if t == 'living_fortress':
        return LivingFortress(cfg.get('grants'))
    # … then in build_unit_ability, add:
    if t=="fights_first":           return FightsFirst()
    if t=="melee_save_retaliate":    return MeleeSaveRetaliate()
    if t=="all_secrets_revealed":    return AllSecretsRevealed()
    if t=="martial_exemplar":        return MartialExemplar()
    if t=="no_hiding_from_watchers": return NoHidingFromTheWatchers()
    if t=="deadly_demise":           return DeadlyDemise(cfg.get("dice"))
    if t=="feel_no_pain":            return FeelNoPain(cfg.get("threshold"))
    if t=="beguiling_form":          return BeguilingForm()
    if t=="daemonic_speed":          return DaemonicSpeed()
    if t=="enthralling_hypnosis":    return EnthrallingHypnosis(cfg.get("aura"))
    if t=="teleport_homer":          return TeleportHomer()
    if t=="fury_of_the_first":       return FuryOfTheFirst()
    if t=="aura_benefit":            return AuraBenefit(cfg["aura"], cfg["benefit"])
    if t=="aura_reroll_wound_1":     return AuraRerollWound1(cfg["aura"])
    if t=="aura_contagion_bonus":    return AuraContagionBonus(cfg["aura"], cfg["bonus"])
    return None


class DatasheetLoader:
    def __init__(self, path='data/datasheets.json'):
        with open(path) as f:
            self.data = json.load(f)

    def get_unit(self, key):
        entry = self.data[key]
        M, T, Sv_raw, Invul_raw, W, Ld_raw, OC_raw = entry['statline']
        Sv = int(str(Sv_raw).rstrip('+'))
        Invul = None if Invul_raw == "-" else int(str(Invul_raw).rstrip('+'))
        Ld = int(str(Ld_raw).rstrip('+'))
        OC = int(str(OC_raw).rstrip('+'))

        # flatten: if it’s already a simple list entry, build it directly
        # Fix ranged weapons
        ranged = []
        for wg in entry.get('ranged_weapons', []):
            if isinstance(wg, list):
                ranged.append(build_weapon(wg, 'ranged'))
            else:
                for prof in wg.get('profiles', []):
                    ranged.append(build_weapon(prof, 'ranged'))  # ← wrap profile here

        # Fix melee weapons
        melee = []
        for wg in entry.get('melee_weapons', []):
            if isinstance(wg, list):
                melee.append(build_weapon(wg, 'melee'))
            else:
                for prof in wg.get('profiles', []):
                    melee.append(build_weapon(prof, 'melee'))  # ← wrap profile here

        unit_abils = []
        for nm,cfg in entry.get('abilities',{}).items():
            a = build_unit_ability(nm,cfg)
            if a: unit_abils.append(a)

        return {
            'size': entry.get('size',1),
            'M': M, 'T': T, 'Sv': Sv, 'W': W,
            'Ld': Ld, 'OC': OC,
            'ranged_weapons': ranged,
            'melee_weapons': melee,
            'wargear_options': entry.get('wargear_options',{}),
            'attachable_leaders': entry.get('attachable_leaders',[]),
            'unit_abilities': unit_abils,
            'specialRules': entry.get('specialRules',{})
        }

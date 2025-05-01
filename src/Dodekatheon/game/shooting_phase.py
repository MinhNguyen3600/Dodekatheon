# Game/shooting_phase.py
import math as _math
from objects.dice import roll_d6
from data.unit_abilities import LoneOperative, DarkAngelsBodyguard
from ..utils import bdr_s, bdr_m, bdr_l

def shooting_phase(game):
    for unit in [u for u in game.current_player().units if u.is_alive() and not u.fell_back]:
        all_weapons = unit.datasheet['ranged_weapons']

        if unit.advanced:
            weaps = [w for w in all_weapons if w['abilities'].is_assault]
            if not weaps:
                print(f"{unit.name} advanced and has no Assault weapons. Cannot shoot.\n")
                continue
            else:
                print(f"{unit.name} advanced — only Assault weapons can be used.")
        else:
            weaps = all_weapons

        bdr_m()
        print(f"Shooting for {unit.name}:")
        bdr_m()

        if not weaps or input(f"Shoot with {unit.name}? (y/n): ").lower() != 'y':
            continue

        # Pick weapon
        idx = 0
        if len(weaps) > 1:
            for i, w in enumerate(weaps):
                print(f"{i}: {w['name']}")
            idx = int(input("Select ranged weapon: "))
        w = weaps[idx]

        enemies = []
        for e in game.other_player().units:
            if not e.is_alive(): continue
            d = game.board.distance_inches(unit.position, e.position)
            if d <= w['range']:
                enemies.append((e, d))

        if not enemies:
            print("No targets in range.\n")
            continue

        # Filter Lone Operative units
        legal = []
        for tgt, d in enemies:
            abil = tgt.datasheet.get('unit_abilities', [])
            is_lone = any(isinstance(a, LoneOperative) for a in abil)
            for a in abil:
                if isinstance(a, DarkAngelsBodyguard) and a.grants_lone(tgt, game.current_player().units, game.board):
                    is_lone = True
            if not (is_lone and d > 12):
                legal.append(tgt)

        for i, (e, d) in enumerate(enemies):
            print(f"{i}: {e.name} at {chr(ord('A') + e.position[0])}{e.position[1]+1} ({d:.1f}\")")
        idx = int(input("Pick target: "))
        tgt, dist = enemies[idx]

        if tgt not in legal:
            print("That target isn’t legal (Lone Operative, out of range).")
            continue

        context = {
            'half_range': dist <= w['range'] / 2,
            'in_engagement': dist <= 1,
            'target_models': tgt.current_models,
            'unit_advanced': unit.advanced,
            'is_monster': False,
        }

        num_attacks = w['abilities'].extra_attacks(w['A'], context)
        num_attacks *= unit.current_models

        hits = 0
        for _ in range(num_attacks):
            die = roll_d6()[0]
            mod = w['abilities'].hit_modifier(context)
            skill = w.get('BS', w.get('WS'))
            if w['BS'] is None:
                hits += 1
            else:
                if die == 6 or die + mod >= skill:
                    hits += 1
                    hits += w['abilities'].on_crit_hit()

        wounds = 0
        for _ in range(hits):
            wdie = roll_d6()[0]
            s, t = w['S'], tgt.datasheet['T']
            need = 2 if s >= 2*t else 3 if s > t else 4 if s == t else 5
            if wdie == 6 or wdie >= need:
                wounds += 1

        failed = 0
        total = 0
        mw_total = 0
        initial_models = tgt.current_models

        for _ in range(wounds):
            wdie = roll_d6()[0]
            if w['abilities'].skip_saves_on_crit_wound() and wdie == 6:
                mw = w['abilities'].mortal_wounds_on_crit(w['D'])
                tgt.take_damage(mw)
                total += mw
                mw_total += mw
                failed += 1
            else:
                svr = roll_d6()[0]
                svt = tgt.datasheet['Sv'] - w['AP']
                if svr < svt:
                    dmg = game.resolve_damage(w['D'])
                    tgt.take_damage(dmg)
                    total += dmg
                    failed += 1

            if not tgt.is_alive():
                print(f"{tgt.name} is destroyed!")
                game.board.clear_position(*tgt.position)
                break

        bdr_s()
        print(f"Hit Rolls: {hits}/{num_attacks}")
        print(f"Wound Rolls: {wounds}/{hits}")
        print(f"Failed Saves: {failed}/{wounds}")
        print(f"Total Damage: {total}, Wounds now {tgt.current_wounds}/{tgt.max_wounds}")
        bdr_s()

        unit._last_num_attacks = num_attacks
        unit._last_hits = hits
        unit.register_damage_dealt(
            dmg=total,
            models_killed=(initial_models - tgt.current_models),
            is_ranged=True,
            is_melee=False,
            mortal_wounds=mw_total
        )

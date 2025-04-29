# Game/shooting_phase.py
import math as _math
from objects.dice import roll_d6
from data.unit_abilities import LoneOperative, DarkAngelsBodyguard

def shooting_phase(game):

    # iterate all alive, non–fell-back units (they may have advanced)
    for unit in [u for u in game.current_player().units if u.is_alive() and not u.fell_back]:
            all_weapons = unit.datasheet['ranged_weapons']

            # If unit advanced, only allow assault weapons
            if unit.advanced:
                weaps = [w for w in all_weapons if w['abilities'].is_assault]
                if not weaps:
                    print(f"{unit.name} advanced and has no Assault weapons. Cannot shoot.\n")
                    continue
                else:
                    print(f"{unit.name} advanced — only Assault weapons can be used.")
            else:
                weaps = all_weapons

            print(f"Shooting for {unit.name}:")
            if not weaps or input(f"Shoot with {unit.name}? (y/n): ").lower()!='y':
                continue

            # pick weapon from the (possibly filtered) list
            idx = 0
            if len(weaps)>1:
                for i,w in enumerate(weaps):
                    print(f"{i}: {w['name']}")
                idx = int(input("Select ranged weapon: "))
            w = weaps[idx]

            # build context to compute range
            # now find ALL enemy units in range
            enemies = []
            for e in game.other_player().units:
                if not e.is_alive(): continue
                d = game.board.distance_inches(unit.position, e.position)
                if d <= w['range']:
                    # also enforce Lone Operative here if you like…
                    enemies.append((e, d))

            if not enemies:
                print("No targets in range.\n")
                continue

            # list them
            for i,(e,d) in enumerate(enemies):
                print(f"{i}: {e.name} at {chr(ord('A')+e.position[0])}{e.position[1]+1} ({d:.1f}\")")
            idx = int(input("Pick target: "))
            tgt, dist = enemies[idx]

            # build context for abilities
            context = {
                'half_range':    dist <= w['range']/2,
                'in_engagement': dist <= 1,
                'target_models': tgt.current_models,
                'unit_advanced': unit.advanced,
                'is_monster':    False,
            }

            legal = []
            # enemies is a list of (unit, distance)
            for tgt, d in enemies:
                # fetch that unit's abilities
                unit_abils = tgt.datasheet.get('unit_abilities', [])

                # static lone-operative
                is_lone = any(isinstance(a, LoneOperative) for a in unit_abils)

                # dynamic grant
                for a in unit_abils:
                    if isinstance(a, DarkAngelsBodyguard) and a.grants_lone(tgt, game.current_player().units, game.board):
                        is_lone = True

                # if it is lone, enforce 12" max
                if is_lone and d > 12:
                    continue
                legal.append(tgt)

            if not legal:
                print("No valid targets (Lone Operative out of range).")
                continue
            tgt = legal[0]   # or let player pick among `legal`

            # determine how many attacks we actually make
            num_attacks = w['abilities'].extra_attacks(w['A'], context)
            # every remaining model in the unit fires its attacks
            num_attacks *= unit.current_models

            # ROLL TO HIT
            hits = 0
            for _ in range(num_attacks):
                die = roll_d6()[0]
                mod = w['abilities'].hit_modifier(context)
                skill = w.get('BS', w.get('WS'))
                if die == 6 or die + mod >= skill:
                    # basic hit
                    hits += 1
                    # plus sustained hits on a crit
                    hits += w['abilities'].on_crit_hit()

            # ROLL TO WOUND
            wounds = 0
            for _ in range(hits):
                wdie = roll_d6()[0]
                s,t = w['S'], tgt.datasheet['T']
                need = 2 if s>=2*t else 3 if s>t else 4 if s==t else 5
                if wdie == 6 or wdie >= need:
                    wounds += 1

            # SAVES & DAMAGE
            failed = 0
            total  = 0
            for _ in range(wounds):
                # devastating wounds: crit‐wounds become mortal
                if w['abilities'].skip_saves_on_crit_wound() and wdie==6:
                    mw = w['abilities'].mortal_wounds_on_crit(w['D'])
                    tgt.take_damage(mw)
                    total += mw; failed += 1
                else:
                    svr = roll_d6()[0]
                    svt = tgt.datasheet['Sv'] - w['AP']
                    if svr < svt:
                        dmg = game.resolve_damage(w['D'])
                        tgt.take_damage(dmg)
                        total += dmg; failed += 1

                # clear corpse immediately
                if not tgt.is_alive():
                    print(f"{tgt.name} is destroyed!")
                    game.board.clear_position(*tgt.position)
                    break

            print(f"Hit Rolls: {hits}/{num_attacks}")
            print(f"Wound Rolls: {wounds}/{hits}")
            print(f"Failed Saves: {failed}/{wounds}")
            print(f"Total Damage: {total}, Wounds now {tgt.current_wounds}/{tgt.max_wounds}")
            print()
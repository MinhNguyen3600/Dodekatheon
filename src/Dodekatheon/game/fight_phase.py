import math as _math
from objects.dice import roll_d6
from data.unit_abilities import LoneOperative, DarkAngelsBodyguard

def fight_phase(game):
    # for each of our units that charged successfully
    for attacker in [u for u in game.current_player().units if u.is_alive() and u.charged]:
        print(f"Fighting for {attacker.name}:")
        weaps = attacker.datasheet['melee_weapons']
        if not weaps or input("Make melee attack? (y/n): ").lower()!='y':
            continue

        # pick melee weapon
        idx = 0
        if len(weaps)>1:
            for i,w in enumerate(weaps):
                print(f"{i}: {w['name']}")
            idx = int(input("Select melee weapon: "))
        w = weaps[idx]

        # gather all enemy units within 1.5"
        enemies = []
        for e in game.other_player().units:
            if not e.is_alive(): continue
            d = game.board.distance_inches(attacker.position, e.position)
            if d <= 1.5:
                enemies.append((e,d))

        if not enemies:
            print("No enemies in melee range.\n")
            continue

        # list them
        for i,(e,d) in enumerate(enemies):
            cx,cy = e.position
            print(f"{i}: {e.name} at {chr(ord('A')+cx)}{cy+1} ({d:.1f}\")")
        pick = int(input("Pick target: "))
        defender, dist = enemies[pick]

        # build ability-context
        context = {
            'half_range':    False,
            'in_engagement': dist <= 1,
            'target_models': defender.current_models,
            'unit_advanced': attacker.advanced,
            'is_monster':    False,
        }

        # determine number of attacks
        rawA = w['A']
        if isinstance(rawA,str) and rawA.startswith('D6'):
            parts = rawA.split('+')
            bonus = int(parts[1]) if len(parts)>1 else 0
            num_attacks = roll_d6()[0] + bonus
        else:
            num_attacks = int(rawA)
        num_attacks = w['abilities'].extra_attacks(num_attacks, context)

        # roll to hit
        hits = 0
        for _ in range(num_attacks):
            die = roll_d6()[0]
            mod = w['abilities'].hit_modifier(context)
            ws = w.get('WS', attacker.datasheet['T'])
            if die==6 or die+mod>=ws:
                hits += 1
                hits += w['abilities'].on_crit_hit()

        # roll to wound
        wounds = 0
        for _ in range(hits):
            wdie = roll_d6()[0]
            s,t = w['S'], defender.datasheet['T']
            need = 2 if s>=2*t else 3 if s>t else 4 if s==t else 5
            if wdie==6 or wdie>=need:
                wounds += 1

        # saves & apply damage
        failed = 0
        total  = 0
        for _ in range(wounds):
            if w['abilities'].skip_saves_on_crit_wound() and wdie==6:
                mw = w['abilities'].mortal_wounds_on_crit(w['D'])
                defender.take_damage(mw)
                total += mw; failed += 1
            else:
                svr = roll_d6()[0]
                svt = defender.datasheet['Sv'] - w['AP']
                if svr < svt:
                    dmg = game.resolve_damage(w['D'])
                    defender.take_damage(dmg)
                    total += dmg; failed += 1

            if not defender.is_alive():
                print(f"{defender.name} is destroyed!")
                game.board.clear_position(*defender.position)
                break

        print(f"Hit Rolls: {hits}/{num_attacks}")
        print(f"Wound Rolls: {wounds}/{hits}")
        print(f"Failed Saves: {failed}/{wounds}")
        print(f"Total Damage: {total}, Wounds now {defender.current_wounds}/{defender.max_wounds}\n")

    return True

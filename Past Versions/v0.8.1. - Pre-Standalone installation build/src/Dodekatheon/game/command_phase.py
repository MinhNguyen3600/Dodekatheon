# game/command_phase.py
import math
from objects.dice import roll_d6

def command_phase(game):
    # STEP 1: both players gain 1 CP
    for p in game.players:
        p.gain_cp(1)

    # STEP 2: Battle-shock tests for current player
    print(f"\n-- Battle-shock tests for {game.current_player().name} --")
    # clear any old battle_shocked flags on your units
    for u in game.current_player().units:
        u.battle_shocked = False

    # test each unit that is below half-strength
    for u in game.current_player().units:
        if not u.is_alive():
            continue
        if not u.below_half_strength:
            continue

        # roll 2D6
        dice = roll_d6(2)
        total = sum(dice)
        leadership = u.datasheet['Ld']
        print(f"  {u.name} below half-strength → roll {dice} = {total} vs Ld {leadership}", end=' ')
        if total < leadership:
            u.battle_shocked = True
            print("→ FAILED → Battle-shocked!")
        else:
            print("→ passed.")

    print()

# game/charge_phase.py

import math as _math

from objects.dice import roll_d6
from data.keywords import has_keyword

from ..utils import *
from ..objective import Objective

def charge_phase(game):
    # ——— allow abilities to react in Charge phase ———
    game.run_choice_abilities('charge')

    # ask once: does the player want to charge or skip?
    while True:
        cmd = input("Enter charge phase ([c]harge/[s]kip): ").lower()
        if cmd == 's':
            confirm = input("Confirm end turn? (y/n): ").lower()
            if confirm == 'y':
                game.current = 1 - game.current
                game.round += 1
                return False
            # if they decline, re‑loop and ask again
            continue
        if cmd == 'c':
            break
        # anything else, re‑ask
    # end skip/confirm loop

    any_moved = False

    # for each eligible unit…
    for u in [u for u in game.current_player().units if u.is_alive() and not u.fell_back]:
        # roll the dice
        charge_dist = sum(roll_d6(2))
        print(f"Charge roll for {u.name}: {charge_dist}\"")

        # compute all squares reachable up to charge_dist
        moves = reachable_squares(u, game.board, charge_dist)
        moves.discard(u.position)

        # only keep those that end within 1" of any alive enemy
        moves = {
            sq for sq in moves
            if any(
                game.board.distance_inches(sq, e.position) <= 1
                for e in game.other_player().units
                if e.is_alive()
            )
        }

        # if this unit has no legal charge, skip it
        if not moves:
            print(f"  {u.name} has no legal charge destinations — skipping.\n")
            continue

        any_moved = True

        # highlight and prompt
        game.board.display(flip=True, highlight=moves)
        while True:
            coord = input(f"Enter charge destination (e.g. E10) for {u.name}: ").strip().upper()

            # parse letter/number split
            for i in range(1, len(coord)):
                col, row_s = coord[:i], coord[i:]
                if not row_s.isdigit():
                    continue
                x = parse_column_label(col)
                y = int(row_s) - 1

                if (x, y) not in moves:
                    print(f"  {coord} is not a valid charge destination.")
                    break

                # perform the charge
                u.charged = True
                game.board.move_unit(u, x, y)
                print(f"{u.name} charged to {coord}\n")
                game.display_state()
                break  # out of for‑i loop

            else:
                # no split produced a valid numeric row
                print("  Could not parse coordinate; try again.")
                continue

            # if we broke out with a successful move, exit the while‑True
            break

    # update objectives after all charges
    Objective.update_objective_control(game)

    # return True if any unit actually charged, False if none did
    return any_moved

import math as _math
from objects.dice import roll_d6
from .movement_phase import reachable_squares

def charge_phase(game):
    # ask whether to charge at all
    if input("Enter charge phase ([c]harge/[s]kip): ").lower()!='c':
        if input("Confirm end turn? (y/n): ").lower()=='y':
            game.current = 1 - game.current
            game.round += 1
            return False
        else:
            return charge_phase(game)

    for u in [u for u in game.current_player().units if u.is_alive() and not u.fell_back]:
        # roll the charge
        charge_dist = sum(roll_d6(2))
        print(f"Charge roll for {u.name}: {charge_dist}\"")

        # compute all squares reachable (including diagonal) up to charge_dist
        moves = reachable_squares(u, game.board, charge_dist)
        # cannot stay in place for a charge
        moves.discard(u.position)

        if not moves:
            print(f"No legal charge destinations for {u.name}.")
            continue

        # highlight just those squares
        game.board.display(flip=True, highlight=moves)

        # prompt for coordinate
        while True:
            coord = input(f"Enter destination (e.g. E10) for {u.name}: ").strip().upper()
            if len(coord) < 2:
                print("Invalid format. Try again.")
                continue
            col = coord[0]
            row_s = coord[1:]
            if not col.isalpha() or not row_s.isdigit():
                print("Invalid format. Letters then numbers. Try again.")
                continue
            x = ord(col) - ord('A')
            y = int(row_s) - 1
            if (x,y) not in moves:
                print(f"{coord} is not a valid charge destination. Choose again.")
                continue
            # perform move
            u.charged = True
            game.board.move_unit(u, x, y)
            # carry any “C” buddies
            if u.symbol=='C':
                for v in game.current_player().units:
                    if v is not u and v.symbol=='C':
                        game.board.clear_position(*v.position)
                        v.position = (x,y)
                        game.board.place_unit(v)
            game.display_state()
            break

    return True

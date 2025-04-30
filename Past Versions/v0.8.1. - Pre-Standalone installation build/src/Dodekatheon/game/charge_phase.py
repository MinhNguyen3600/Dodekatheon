import math as _math
from objects.dice import roll_d6
from .movement_phase import reachable_squares, parse_column_label

def parse_column_label(label):
    """Convert Excel-style column label (A, B, ..., Z, AA, AB...) to 0-based index"""
    total = 0
    for c in label:
        if not ('A' <= c <= 'Z'):
            raise ValueError("Invalid column letter")
        total = total * 26 + (ord(c) - ord('A') + 1)
    return total - 1


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
            for i in range(1, len(coord)):
                col_label, row_s = coord[:i], coord[i:]
                if row_s.isdigit():
                    try:
                        x = parse_column_label(col_label)
                        y = int(row_s) - 1
                        if (x, y) not in moves:
                            print(f"{coord} is not a valid charge destination. Choose again.")
                            break
                        u.charged = True
                        game.board.move_unit(u, x, y)
                        if u.symbol == 'C':
                            for v in game.current_player().units:
                                if v is not u and v.symbol == 'C':
                                    game.board.clear_position(*v.position)
                                    v.position = (x, y)
                                    game.board.place_unit(v)
                        game.display_state()
                        break
                    except ValueError:
                        print("Invalid coordinate. Try again.")
                        break
            else:
                print("Invalid format. Try again.")
                continue
            break

    return True

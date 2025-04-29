# movement_phase.py
import math as _math
from objects.dice import roll_d6
from .utils import reachable_squares, parse_column_label    # or wherever you put it

def movement_phase(self):
    for u in [u for u in self.current_player().units if u.is_alive()]:
        base = u.datasheet['M']
        choice = input(f"{u.name} move [n]ormal/[a]dv/[f]all/[s]tationary: ").lower()
        if choice == 'a':
            boost = roll_d6()[0]
            print(f"Advance roll: {boost}")
            max_move = base + boost; u.advanced = True
        elif choice == 'f':
            max_move = base; u.fell_back = True
        elif choice == 's':
            max_move = 0
        else:
            max_move = base

        # compute all reachable squares
        moves = reachable_squares(u, self.board, max_move)
        moves.discard(u.position)
        if not moves:
            print("No valid moves for this unit.")
            continue

        # show board with only those squares highlighted
        self.board.display(flip=True, highlight=moves)

        # now prompt until they give a legal square code
        while True:
            code = input("Enter destination (e.g. E10): ").strip().upper()
            for i in range(1, len(code)):
                col_label, row_s = code[:i], code[i:]
                if row_s.isdigit():
                    try:
                        x = parse_column_label(col_label)
                        y = int(row_s) - 1
                        if not (0 <= x < self.board.width and 0 <= y < self.board.height):
                            raise ValueError
                        if (x, y) not in moves:
                            print("That square is not reachable this move.")
                            break
                        # legal
                        self.board.move_unit(u, x, y)
                        print(f"{u.name} moved to {col_label}{row_s}\n")
                        self.board.display(flip=True)
                        break
                    except ValueError:
                        print("Invalid coordinate. Try again.")
                        break
            else:
                print("Invalid format. Try again.")
                continue
            break

        # # perform the move
        # self.board.move_unit(u, x, y)
        # print(f"{u.name} moved to {col}{row}\n")
        # # redisplay full un-gridded board
        # self.board.display(flip=True)
    
# movement_phase.py
import math as _math
from objects.dice import roll_d6
from .utils import reachable_squares    # or wherever you put it

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
            if len(code) < 2:
                print("Bad format, try again."); continue
            col = code[0]
            row_s = code[1:]
            if not ('A' <= col < chr(ord('A')+self.board.width)):
                print("Column out of range."); continue
            if not row_s.isdigit():
                print("Row must be a number."); continue
            row = int(row_s)
            x = ord(col) - ord('A')
            y = row - 1
            if not (0 <= x < self.board.width and 0 <= y < self.board.height):
                print("That square is off-board."); continue
            if (x,y) not in moves:
                print("That square is not reachable this move."); continue
            # legal!
            break

        # perform the move
        self.board.move_unit(u, x, y)
        print(f"{u.name} moved to {col}{row}\n")
        # redisplay full un-gridded board
        self.board.display(flip=True)
    
# movement_phase.py
import math as _math
from objects.dice import roll_d6
from .utils import reachable_squares, parse_column_label    # your helper to turn "AA"->int

ENGAGEMENT_RANGE = 1.0

def movement_phase(self):
    for u in [u for u in self.current_player().units if u.is_alive()]:
        base = u.datasheet['M']
        choice = input(f"{u.name} move [n]ormal/[a]dv/[f]all/[s]tationary: ").lower()

        # reset flags each turn
        u.advanced = False
        u.fell_back = False

        if choice == 'a':
            boost = roll_d6()[0]
            print(f"Advance roll: {boost}")
            max_move = base + boost
            u.advanced = True

        elif choice == 'f':
            max_move = base
            u.fell_back = True

            # if Battle-shocked, take one Desperate Escape test per model
            if getattr(u, 'battle_shocked', False):
                tests = u.current_models
                print(f"  {u.name} is Battle-shocked! -> Taking Desperate Escape tests for {tests}")
                for i in range(1, tests+1):
                    d = roll_d6()[0]
                    if d <= 2:
                        print(f"    Test {i}: {d} -> One model lost")
                        # subtract one model's worth of wounds
                        u.take_damage(u.wounds_per_model)
                print(f"  -> now {u.current_models}/{u.size} models remain\n")

        else:
            # stationary or any other input
            max_move = 0 if choice == 's' else base

        # compute reachable squares
        if u.fell_back:
            # Fall-back: any square ≤ max_move, but cannot end in Engagement Range of any enemy
            moves = set()
            cx, cy = u.position
            for x in range(self.board.width):
                for y in range(self.board.height):
                    # distance check
                    if self.board.distance_inches((cx, cy), (x, y)) <= max_move:
                        # must end on empty or its own start
                        if (x,y) == (cx,cy) or self.board.grid[y][x] == ' ':
                            # ensure not within ER of any enemy
                            too_close = False
                            for opp in self.other_player().units:
                                if not opp.is_alive(): continue
                                if self.board.distance_inches((x,y), opp.position) <= ENGAGEMENT_RANGE:
                                    too_close = True
                                    break
                            if not too_close:
                                moves.add((x,y))
        else:
            # Normal or Advance or Stationary
            moves = reachable_squares(u, self.board, max_move)

        # never include starting square
        moves.discard(u.position)

        if not moves:
            print("No valid moves for this unit.\n")
            continue

        # show board with only those squares highlighted
        self.board.display(flip=True, highlight=moves)

        # prompt until a legal destination is entered
        while True:
            code = input("Enter destination (e.g. E10): ").strip().upper()
            # split between letters and digits
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
                        # perform the move
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
            # exit the outer while once move succeeded
            break
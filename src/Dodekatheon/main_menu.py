# src/dodekatheon/game/main_menu.py

import sys
from data.datasheet_loader import DatasheetLoader
from game.unit_builder import build_army
from game.game import Game
from objects.player import Player
from game.utils import parse_column_label

def do_new_game():
    loader = DatasheetLoader()

    print("\n=== Build Player 1’s army ===")
    p1_units = build_army(loader)
    print("\n=== Build Player 2’s army ===")
    p2_units = build_army(loader)

    # wrap into Player objects
    P1 = Player("P1")
    for u in p1_units:
        P1.add_unit(u)
    P2 = Player("P2")
    for u in p2_units:
        P2.add_unit(u)

    # create game
    game = Game(P1, P2)

    # placement phase
    for pl in (P1, P2):
        print(f"\n{pl.name}, place your units on the board:")
        game.board.display(flip=True)
        for u in pl.units:
            while True:
                code = input(f"  Where place {u.name} (e.g. A1): ").strip().upper()
                # try every possible split between letters and digits
                for i in range(1, len(code)):
                    col_label, row_s = code[:i], code[i:]
                    if row_s.isdigit():
                        try:
                            x = parse_column_label(col_label)
                            y = int(row_s) - 1
                            # bounds check
                            if not (0 <= x < game.board.width and 0 <= y < game.board.height):
                                raise ValueError("off board")
                            # occupancy check
                            if game.board.grid[y][x] != ' ':
                                print("    That square is occupied; choose another.")
                                raise ValueError
                            # place it
                            u.position = (x, y)
                            game.board.place_unit(u)
                            game.board.display(flip=True)
                            raise StopIteration          # exit both loops
                        except StopIteration:
                            break
                        except Exception:
                            # any error, ask again
                            break
                else:
                    print("    Bad format.  Letters (A…Z,AA…) then digits.  Try again.")
                    continue
                # if we broke out successfully, go to next unit
                if game.board.grid[y][x] == u.symbol:
                    break

    print("\nAll units placed.  Let the battle begin!\n")

    # play loop
    while not game.is_over():
        game.play_turn()

    print(f"\nGame over! {game.other_player().name} wins!\n")
    from game.scoreboard import print_scoreboard
    print_scoreboard(game)
    input("Press ENTER to exit…")

def main_menu():
    while True:
        print("\n=== W40k-Dodekatheon ===")
        print("1) New Game")
        print("2) Quit")
        choice = input("Select an option: ").strip()
        if choice == '1':
            do_new_game()
        elif choice == '2':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection.  Please choose 1 or 2.")

if __name__ == "__main__":
    main_menu()

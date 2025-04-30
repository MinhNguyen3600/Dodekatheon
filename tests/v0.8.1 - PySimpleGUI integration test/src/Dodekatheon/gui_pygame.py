# src/dodekatheon/gui_pygame.py

import sys
import pygame
from data.datasheet_loader import DatasheetLoader
from objects.player       import Player
from objects.unit         import Unit
from game.game            import Game
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
CELL_SIZE = 40    # pixels per grid‐cell
MARGIN    = 20    # pixels around the board

def make_test_game():
    loader = DatasheetLoader()
    # load some datasheets
    ds_guard = loader.get_unit("Custodian Guard")
    ds_lion  = loader.get_unit("Lion El'Johnson")

    # make units
    u1 = Unit("Guard1", 'C', 0, 0, ds_guard)
    u2 = Unit("Lion",  'L', 5, 5, ds_lion)

    # players
    p1 = Player("P1"); p1.add_unit(u1)
    p2 = Player("P2"); p2.add_unit(u2)

    return Game(p1,p2)

def grid_to_pixel(x, y):
    """Convert board coords → pixel rect."""
    px = MARGIN + x * CELL_SIZE
    py = MARGIN + (game.board.height-1 - y) * CELL_SIZE
    return pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)

def draw_board(screen, game):
    screen.fill((30,30,30))
    # draw cells
    for y in range(game.board.height):
        for x in range(game.board.width):
            rect = grid_to_pixel(x,y)
            pygame.draw.rect(screen, (50,50,50), rect, 1)
    # draw units
    for p in game.players:
        for u in p.units:
            if u.is_alive():
                rect = grid_to_pixel(*u.position)
                # choose color by symbol
                color = (200,50,50) if p is game.current_player() else (50,200,50)
                pygame.draw.circle(screen, color, rect.center, CELL_SIZE//3)
                # draw symbol letter
                font = pygame.font.SysFont(None, 24)
                img  = font.render(u.symbol, True, (255,255,255))
                screen.blit(img, (rect.x+4, rect.y+4))

def main():
    global game
    pygame.init()
    game = make_test_game()

    w = MARGIN*2 + game.board.width  * CELL_SIZE
    h = MARGIN*2 + game.board.height * CELL_SIZE
    screen = pygame.display.set_mode((w,h))
    pygame.display.set_caption("40k Dodekatheon")

    selected = None

    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx,my = ev.pos
                # convert pixel → board coords
                bx = (mx - MARGIN) // CELL_SIZE
                by = game.board.height-1 - ((my - MARGIN) // CELL_SIZE)
                if 0 <= bx < game.board.width and 0 <= by < game.board.height:
                    # click on a unit?
                    for u in game.current_player().units:
                        if u.position == (bx,by) and u.is_alive():
                            selected = u
                            break
                    else:
                        # if clicked empty square and we have a selection, move there
                        if selected:
                            # check reachable (you can integrate your reachable_squares)
                            # for now, just move unconditionally:
                            game.board.move_unit(selected, bx, by)
                            selected = None
                            # advance turn
                            game.play_turn()

        draw_board(screen, game)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()

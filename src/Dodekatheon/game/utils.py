# src/wh40kgame/game/utils.py

def reachable_squares(unit, board, max_dist):
    """
    Return set of (x,y) on board within Euclidean distance ≤ max_dist from unit.position.
    """
    cx, cy = unit.position
    valid = set()
    for x in range(board.width):
        for y in range(board.height):
            # only consider empty squares or the unit’s own square
            if board.grid[y][x] == ' ' or (x, y) == unit.position:
                if board.distance_inches((cx, cy), (x, y)) <= max_dist:
                    valid.add((x, y))
    return valid

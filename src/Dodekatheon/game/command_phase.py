# Game/command_phase.py
def command_phase(game):
    """
    Both players gain 1 CP.
    """
    for p in game.players:
        p.gain_cp(1)

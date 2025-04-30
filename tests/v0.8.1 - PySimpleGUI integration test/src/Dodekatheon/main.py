# main.py
from data.datasheet_loader import DatasheetLoader
from objects.player import Player
from objects.unit import Unit
from game.game import Game

loader = DatasheetLoader()

# Units loader
ds_cGuard = loader.get_unit("Custodian Guard")
ds_lion = loader.get_unit("Lion El'Johnson")
ds_termie = loader.get_unit("Terminator Squad")
ds_angron = loader.get_unit("Angron")
ds_morty = loader.get_unit("Mortarion")
ds_fulgrim = loader.get_unit("Fulgrim")

# Assign unit start location
unit_C1 = Unit("Custodian Squad 1", 'C', 0, 0, ds_cGuard)
# unit_C1 = Unit("Custodian Squad 1", 'C', 1, 0, ds_cGuard)
# unit_C1 = Unit("Custodian Squad 1", 'C', 32, 24, ds_cGuard)
# unit_C1 = Unit("Custodian Squad 1", 'C', 31, 24, ds_cGuard)


# unit_C2 = Unit("Custodian Squad 2", 'S', 0, 0, ds_cGuard)
unit_C2 = Unit("Custodian Squad 2", 'S', 1, 0, ds_cGuard)
# unit_C2 = Unit("Custodian Squad 2", 'S', 32, 24, ds_cGuard)
# unit_C2 = Unit("Custodian Squad 2", 'S', 31, 24, ds_cGuard)

# unit_L = Unit("Lion El'Johnson", 'L', 0, 0, ds_lion)
# unit_L = Unit("Lion El'Johnson", 'L', 1, 0, ds_lion)
unit_L = Unit("Lion El'Johnson", 'L', 5, 5, ds_lion)
# unit_L = Unit("Lion El'Johnson", 'L', 32, 24, ds_lion)
# unit_L = Unit("Lion El'Johnson", 'L', 31, 24, ds_lion)

# unit_T = Unit("Terminator Squad", 'T', 0, 0, ds_termie)
# unit_T = Unit("Terminator Squad", 'T', 1, 0, ds_termie)
# unit_T = Unit("Terminator Squad", 'T', 32, 24, ds_termie)
# unit_T = Unit("Terminator Squad", 'T', 31, 24, ds_termie)

# unit_A = Unit("Angron", 'A', 0, 0, ds_angron)
# unit_A = Unit("Angron", 'A', 1, 0, ds_angron)
# unit_A = Unit("Angron", 'A', 31, 24, ds_angron)
unit_A = Unit("Angron", 'A', 30, 15, ds_angron)

# unit_M = Unit("Mortarion", 'M', 4, 0, ds_morty)
# unit_M = Unit("Mortarion", 'M', 1, 0, ds_morty)
# unit_M = Unit("Mortarion", 'M', 31, 24, ds_morty)
# unit_M = Unit("Mortarion", 'M', 32, 24, ds_morty)

# unit_F = Unit("Fulgrim", 'F', 0, 0, ds_fulgrim)
# unit_F = Unit("Fulgrim", 'F', 1, 0, ds_fulgrim)
# unit_F = Unit("Fulgrim", 'F', 31, 24, ds_fulgrim)
# unit_F = Unit("Fulgrim", 'F', 32, 24, ds_fulgrim)

# Player 1
p1 = Player("P1")
# p1.add_unit(unit_A)
# p1.add_unit(unit_M)
p1.add_unit(unit_L)
# p1.add_unit(unit_T)
p1.add_unit(unit_C1)
p1.add_unit(unit_C2)
# p1.add_unit(unit_F)

# Player 2
p2 = Player("P2")
p2.add_unit(unit_A)
# p2.add_unit(unit_M)
# p2.add_unit(unit_L)
# p2.add_unit(unit_T)
# p2.add_unit(unit_C1)
# p2.add_unit(unit_C2)
# p2.add_unit(unit_F)

# Player 2: single Custodian squad (4 Guards + Shield Captain)
# Combine Guard + Captain datasheets into one squad
# guard_ds = loader.get_unit("Custodian Guard")
# captain_ds = loader.get_unit("Shield Captain")
# # Merge weapons
# squad_ds = {
#     'M': guard_ds['M'], 'T': guard_ds['T'], 'Sv': guard_ds['Sv'], 'W': guard_ds['W'],
#     'Ld': guard_ds['Ld'], 'OC': guard_ds['OC'],
#     'ranged_weapons': guard_ds['ranged_weapons'] + captain_ds['ranged_weapons'],
#     'melee_weapons': guard_ds['melee_weapons'] + captain_ds['melee_weapons'],
#     'abilities': {**guard_ds['abilities'], **captain_ds['abilities']}
# }


# Start game
game = Game(p1, p2)
while not game.is_over():
    game.play_turn()
print(f"Game over! {game.other_player().name} wins!")

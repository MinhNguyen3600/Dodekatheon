# # ------------------------------
# # File: customizer.py
# # ------------------------------
# import json
# from unit import Unit
# from player import Player

# # Load datasheets
# with open('datasheets.json') as f:
#     DATASHEETS = json.load(f)


# def choose_unit_forge():
#     print("Available unit types:")
#     for i, key in enumerate(DATASHEETS.keys(), 1):
#         print(f"{i}. {key}")
#     choice = int(input("Select unit type: ")) - 1
#     unit_key = list(DATASHEETS.keys())[choice]
#     data = DATASHEETS[unit_key]

#     # choose size
#     sizes = data['options']['unit_size']
#     print(f"Available sizes: {sizes}")
#     size = int(input(f"Select unit size {sizes}: "))

#     # instantiate player and add units
#     p = Player("Custom P")
#     for n in range(size):
#         # default wargear: first listed weapon for each model
#         ws_name, ws_stats = next(iter(data['weapons'].items()))
#         datasheet = {**data['stats'], **ws_stats}
#         u = Unit(data['unit_name'], symbol=unit_key[0], x=0, y=0, datasheet=datasheet)
#         p.add_unit(u)
#     return p


# if __name__ == '__main__':
#     player = choose_unit_forge()
#     print(f"Created {len(player.units)} models of type {player.units[0].name}")
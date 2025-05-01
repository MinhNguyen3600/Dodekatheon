from objects.unit import Unit

def build_unit(key, loader):
    ds = loader.get_unit(key)
    u = Unit(key, symbol=key[0], x=0,y=0, datasheet=ds)
    # let user pick wargear
    u.choose_wargear()
    # optionally attach a leader
    if ds['attachable_leaders']:
        print("You may attach:")
        for i,l in enumerate(ds['attachable_leaders']):
            print(f"  {i}: {l}")
        pick = input("Pick leader or ENTER for none: ")
        if pick.isdigit():
            leader_ds = loader.get_unit(ds['attachable_leaders'][int(pick)])
            leader = Unit(ds['attachable_leaders'][int(pick)], l[0],0,0,leader_ds)
            u.attach_leader(leader)
    return u

def build_army(loader):
    army = []
    print("Available units:")
    for i,k in enumerate(loader.data.keys()):
        print(f"  {i}: {k}")
    while True:
        pick = input("Add unit by number or ENTER to finish: ")
        if not pick:
            break
        key = list(loader.data.keys())[int(pick)]
        u = build_unit(key, loader)
        army.append(u)
    return army

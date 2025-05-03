from objects.unit import Unit
from data.keywords import can_attach_to_army

def build_unit(key, loader, army_faction):
    ds = loader.get_unit(key)

    # enforce faction keyword legality
    if not can_attach_to_army(ds, army_faction):
        raise ValueError(f"{key} is not legal in a {army_faction} army.")

    u = Unit(key, symbol=key[0], x=0, y=0, datasheet=ds)

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
            leader = Unit(ds['attachable_leaders'][int(pick)], symbol=l[0], x=0, y=0, datasheet=leader_ds)
            u.attach_leader(leader)
    return u

def build_army(loader):
    army = []
    # 1) pick primary faction
    primaries = sorted({ loader.get_unit(k)['keywords']['faction'][0]
                         for k in loader.data.keys() })
    print("Choose your primary faction:")
    for i,f in enumerate(primaries):
        print(f"  {i}: {f}")
    p = int(input("Primary faction #: "))
    primary = primaries[p]

    # 2) pick secondary faction (if any)
    #   collect all second-position faction keywords among units of this primary
    secs = sorted({ ds['keywords']['faction'][1]
                    for k,ds in ((k,loader.get_unit(k)) for k in loader.data.keys())
                    if ds['keywords']['faction'][0]==primary
                      and len(ds['keywords']['faction'])>1 })
    if secs:
        print(f"Choose your sub-faction within {primary}:")
        for i,f in enumerate(secs):
            print(f"  {i}: {f}")
        s = int(input("Sub-faction #: "))
        secondary = secs[s]
    else:
        secondary = None

    print(f"\nBuilding army for {primary}",
           (f" - sub-faction {secondary}" if secondary else ""),  "\n")

    # 3) now list only units matching your choice
    candidates = [ k for k in loader.data.keys()
                   if loader.get_unit(k)['keywords']['faction'][0]==primary
                   and (secondary is None
                        or ( len(loader.get_unit(k)['keywords']['faction'])>1
                             and loader.get_unit(k)['keywords']['faction'][1]==secondary )) ]

    while True:
        print("\nAvailable units:")
        for i,k in enumerate(candidates):
            print(f"  {i}: {k}")
        pick = input("Add unit by number or ENTER to finish: ")
        if not pick:
            break
        key = candidates[int(pick)]
        u = build_unit(key, loader, primary)
        army.append(u)
    return army

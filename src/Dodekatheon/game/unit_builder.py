from objects.unit import Unit
from data.keywords import can_attach_to_army
from data.datasheet_loader import DatasheetLoader


def build_unit(key, loader, army_faction):
    ds = loader.get_unit(key)

    # enforce faction keyword legality
    if not can_attach_to_army(ds, army_faction):
        raise ValueError(f"{key} is not legal in a {army_faction} army.")

    # # --- handle unit size choices ---
    # comp = ds.get('unit_composition', {})

    # # new style: min/max
    # if 'min' in comp and 'max' in comp:
    #     while True:
    #         try:
    #             n = int(input(f"Choose unit size [{comp['min']}-{comp['max']}]: "))
    #             if comp['min'] <= n <= comp['max']:
    #                 ds['size'] = n
    #                 break
    #         except ValueError:
    #             pass
    #         print("Invalid size; try again.")
    # # legacy style: size_options
    # elif comp.get('size_options') and len(comp['size_options'])>1:
    #     # (your existing size_options logic…)
    #     size_opts = comp['size_options']
    #     while True:
    #         print(f"\nChoose size for {key}:")
    #         for i,opt in enumerate(size_opts):
    #             cnt = opt.get('count', ds['size'])
    #             mand = opt.get('mandatory', [])
    #             print(f"  {i}: {cnt} models, mandatory: {mand}")
    #         try:
    #             choice = int(input("Size option #: "))
    #             if 0 <= choice < len(size_opts):
    #                 ds['size'] = size_opts[choice]['count']
    #                 break
    #         except ValueError:
    #             pass
    #         print("Invalid choice; try again.")

    # create the Unit instance
    u = Unit(key, symbol=key[0], x=0, y=0, datasheet=ds)

    # immediately let user customize this unit’s wargear & composition
    if ds.get('unit_composition') or ds.get('wargear_options'):
        print(f"\nCustomize {u.name}:")
        u.choose_wargear()

    # optionally attach a leader
    if ds['attachable_leaders']:
        print("You may attach:")
        for i,l in enumerate(ds['attachable_leaders']):
            print(f"  {i}: {l}")
        pick = input("Pick leader index or ENTER for none: ")   
        if pick.isdigit():
            lk = ds['attachable_leaders'][int(pick)]
            leader_ds = loader.get_unit(lk)
            leader    = Unit(lk, symbol=lk[0], x=0, y=0, datasheet=leader_ds)
            u.attach_leader(leader)

            # let the player customize the attached Shield-Captain too:
            print(f"\nCustomize attached {leader.name}:")
            leader.choose_wargear()
    return u

def build_army(loader):
    army = []

    # 1) pick primary faction (only the first entry of each unit's faction list)
    #    but skip any JSON entries that are null
    primaries = sorted({
        loader.get_unit(k)['keywords']['faction'][0]
        for k in loader.data.keys()
        if loader.data[k] is not None
    })

    print("----------------------------")
    print("Choose your PRIMARY faction:")
    print("----------------------------")
    for i,f in enumerate(primaries):
        print(f"  {i}: {f}")

    print("---------------------")
    p = int(input("Primary faction #: "))
    primary = primaries[p]
    print("---------------------")

    # 2) pick sub-faction (or “Space Marine” = no sub)
    #    collect all second-position faction keywords among units of this primary
    secs = sorted({ 
        ds['keywords']['faction'][1]    # secs = secondaries
        for k,ds in ((k,loader.get_unit(k)) for k in loader.data.keys())
            if ds['keywords']['faction'][0] == primary 
            and len(ds['keywords']['faction']) > 1 })

    # make sure subfaction always exists
    

    # 3) prompt for subfaction if any
    if secs:
        subs = [None] + secs
        print(f"\nBuilding army for PRIMARY FACTION [{primary}]")
        print("Pick a Sub-faction")
        print("---------------------")
        
        for i,sub in enumerate(subs):
            # display “0: <primary>” when sub is None
            if sub is not None:
                label = sub 
            else:
                label = primary
            print(f"  {i}: {label}")
            
        s = int(input("Sub-faction #: "))
        subfaction = subs[s]
        print(f"\nBuilding Army for PRIMARY FACTION [{primary}'s] SUB-FACTION [{subfaction or primary}]\n")

    else:
        subfaction = None
        print(f"\nBuilding Army for PRIMARY FACTION [{primary}]\n")


    # 4) build the candidates list
    candidates = []
    for k in loader.data.keys():

        # Load faction keywords
        unit_factions = loader.get_unit(k)['keywords']['faction']

        if unit_factions[0] != primary:
            continue  # not from the primary faction

        # Keep all pure primary units
        if len(unit_factions) == 1:
            candidates.append(k)
        # Include sub-faction match ONLY if chosen and valid
        elif subfaction and unit_factions[1] == subfaction:
            candidates.append(k)
    
    # 5) now display them, tagging those that actually have the chosen subfaction
    while True:
        print("Available units:")

        for i, key in enumerate(candidates):
            facs = loader.get_unit(key)['keywords']['faction']
            tag = (f"[{subfaction}]" 
                   if subfaction and len(facs)>1 and facs[1]==subfaction
                   else f"[{primary}]")
            print(f"  {i}: {tag} {key}")

        pick = input("Add unit by number or ENTER to finish: ")
        if not pick:
            break

        key = candidates[int(pick)]
        u = build_unit(key, loader, primary)
        army.append(u)

    return army


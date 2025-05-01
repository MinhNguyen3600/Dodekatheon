# game/scoreboard.py

def _percent(n, d):
    return f"{int(100 * n / d)}%" if d>0 else "-"

def print_scoreboard(game):
    print("\n" + "="*30 + "  FINAL SCOREBOARD  " + "="*30 + "\n")

    # Per-unit table header
    hdr = [
      "Unit (ID)",
      "Rng Fired","Rng Hits","Rng %", 
      "Mle Fired","Mle Hits","Mle %", 
      "Mort Wnds","Dmg Dealt","Models Kld","CP Spent"
    ]
    rows = []
    for p in game.players:
        print(f"-- {p.name} Units --")
        for u in p.units:
            s = u.stats
            rows.append([
                f"{u.name} ({u.id})",
                s['rng_fired'], s['rng_hits'], _percent(s['rng_hits'], s['rng_fired']),
                s['melee_fired'], s['melee_hits'], _percent(s['melee_hits'], s['melee_fired']),
                s['mortal_wounds'],
                s['damage_dealt'],
                s['models_killed'],
                s['cp_spent']
            ])
        # print this player’s block
        # compute column widths
        widths = [ max(len(str(r[i])) for r in [hdr]+rows) for i in range(len(hdr)) ]
        # print header
        line = "  ".join(hdr[i].ljust(widths[i]) for i in range(len(hdr)))
        print(line)
        print("-"*len(line))
        for r in rows:
            print("  ".join(str(r[i]).ljust(widths[i]) for i in range(len(r))))
        print()
        rows.clear()

    # Per-player summary
    print("-- Player Totals --")
    phdr = ["Player","Dmg","Models Kld","Rng %","Mle %","Mort Wnds","VP","CP Spent","CP Remain"]
    prows = []
    for p in game.players:
        # sum stats
        dmg = sum(u.stats['damage_dealt'] for u in p.units)
        mk  = sum(u.stats['models_killed']  for u in p.units)
        rf, rh = sum(u.stats['rng_fired'] for u in p.units), sum(u.stats['rng_hits'] for u in p.units)
        mf, mh = sum(u.stats['melee_fired'] for u in p.units), sum(u.stats['melee_hits'] for u in p.units)
        mw = sum(u.stats['mortal_wounds'] for u in p.units)
        prows.append([
            p.name, dmg, mk,
            _percent(rh, rf), _percent(mh, mf),
            mw,
            p.victory_points if hasattr(p,"victory_points") else "-", 
            sum(u.stats['cp_spent'] for u in p.units),
            p.cp
        ])
    widths = [ max(len(phdr[i]), *(len(str(r[i])) for r in prows)) for i in range(len(phdr)) ]
    line = "  ".join(phdr[i].ljust(widths[i]) for i in range(len(phdr)))
    print(line)
    print("-"*len(line))
    for r in prows:
        print("  ".join(str(r[i]).ljust(widths[i]) for i in range(len(r))))
    print()

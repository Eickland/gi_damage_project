#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.cyno_yae_odette_valera.rosters
         python -m gi_damage.teams.cyno_yae_odette_valera.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.cyno_yae_odette_valera.builds import (
    BASE_NAME, MAIN_ATK, MAIN_EM, MAIN_ELECTRO, all_teams, make_team,
    odette_build)
from gi_damage.visual.rosters import RosterBook


def main(argv: list[str]) -> int:
    details = "--details" in argv
    book = RosterBook()

    for team in all_teams().values():
        result = team.compute()
        print(team_summary(result))
        if details:
            print(source_breakdown(result))
            print()
            print(hit_details(result))
            print()

    # Главные статы в карточках ростера не различимы — сравниваем текстом
    mains = (("АТК/АТК/крит", MAIN_ATK), ("МС/АТК/крит", MAIN_EM),
             ("АТК/электро/крит", MAIN_ELECTRO))
    for who, key in (("Сайно", "cyno_main_stats"), ("Яэ Мико", "yae_main_stats")):
        print(f"=== Главные статы: {who} ===")
        for label, main in mains:
            r = make_team(label, **{key: main}).compute()
            print(f"{label:<18} DPR {r.dpr:>12,.0f}  DPS {r.dps:>10,.0f}")
        print()

    base = make_team(BASE_NAME)

    book.add(Roster(base, [Variation(slot="Яэ Мико", constellations=[1, 2, 6])]),
             "Созвездия Яэ", ascending=True)
    book.add(Roster(base, [Variation(slot="Сайно", constellations=[1, 2, 6])]),
             "Созвездия Сайно", ascending=True)
    book.add(Roster(base, [Variation(slot="Одетта", builds=[
        odette_build(constellation=c) for c in (0, 1, 2, 4, 6)])]),
             "Созвездия Одетты", ascending=True)
    book.add(Roster(base, [Variation(slot="Валера", constellations=[0, 2, 6])]),
             "Созвездия Валеры", ascending=True)

    book.save("rosters.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

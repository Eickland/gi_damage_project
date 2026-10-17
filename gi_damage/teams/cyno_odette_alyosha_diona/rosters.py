#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.cyno_odette_alyosha_diona.rosters
         python -m gi_damage.teams.cyno_odette_alyosha_diona.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import compare, hit_details, source_breakdown, team_summary
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.cyno_odette_alyosha_diona.builds import (
    BASE_NAME, CYNO_MAIN_ATK, CYNO_MAIN_EM, CYNO_MAIN_ELECTRO,
    all_teams, make_team, odette_build, alyosha_build)
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

    base = make_team(BASE_NAME)

    book.add(Roster(base, [Variation(slot="Сайно", constellations=[1, 2, 6])]),
             "Созвездия Сайно", ascending=True)
    book.add(Roster(base, [Variation(slot="Сайно",
                                     weapons=[DEATHMATCH.at(r) for r in (1, 3, 5)])]),
             "Оружие Сайно", ascending=True)
    # Главные статы в карточках ростера не различимы — сравниваем текстом
    print("=== Главные статы Сайно ===")
    for label, main in (("АТК/АТК/крит", CYNO_MAIN_ATK), ("МС/АТК/крит", CYNO_MAIN_EM),
                        ("АТК/электро/крит", CYNO_MAIN_ELECTRO)):
        r = make_team(label, cyno_main_stats=main).compute()
        print(f"{label:<18} DPR {r.dpr:>12,.0f}  DPS {r.dps:>10,.0f}")
    print()

    book.add(Roster(base, [Variation(slot="Одетта", builds=[
        odette_build(constellation=c) for c in (0, 1, 2, 4, 6)])]),
             "Созвездия Одетты", ascending=True)
    book.add(Roster(base, [Variation(slot="Алеша", builds=[
        alyosha_build(constellation=c) for c in (2, 3, 6)])]),
             "Созвездия Алеши", ascending=True)

    book.save("rosters.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

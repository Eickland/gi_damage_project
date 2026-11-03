#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.mitya_odette_yae_valera.rosters
         python -m gi_damage.teams.mitya_odette_yae_valera.rosters --details
         python -m gi_damage.teams.mitya_odette_yae_valera.rosters --out rosters.html
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.mitya_odette_yae_valera.builds import (
    BASE_NAME, MAIN_EM, MAIN_EM_ELECTRO, MITYA_DISENCHANTMENT, MITYA_EM_2_2,
    all_teams, make_team, odette_build)
from gi_damage.visual.rosters import RosterBook


def main(argv: list[str]) -> int:
    details = "--details" in argv
    out = argv[argv.index("--out") + 1] if "--out" in argv else "rosters.html"
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
    print("=== Главные статы Мити ===")
    for label, main in (("МС/МС/крит", MAIN_EM), ("МС/электро/крит", MAIN_EM_ELECTRO)):
        r = make_team(label, mitya_main_stats=main).compute()
        print(f"{label:<18} DPR {r.dpr:>12,.0f}  DPS {r.dps:>10,.0f}")
    print()

    base = make_team(BASE_NAME)

    book.add(Roster(base, [Variation(slot="Митя", constellations=[0, 1, 2, 4, 5, 6])]),
             "Созвездия Мити", ascending=True)
    book.add(Roster(base, [Variation(slot="Митя", weapons=[
        SPINDLELUTE, STARSEALED.at(1), STARSEALED.at(5)])]),
             "Оружие Мити", ascending=True)
    book.add(Roster(base, [Variation(slot="Митя", artifact_sets=[
        MITYA_DISENCHANTMENT, MITYA_EM_2_2])]),
             "Артефакты Мити", ascending=True)
    book.add(Roster(base, [Variation(slot="Валера", constellations=[0, 2, 6])]),
             "Созвездия Валеры", ascending=True)
    book.add(Roster(base, [Variation(slot="Одетта", builds=[
        odette_build(constellation=c) for c in (0, 1, 2, 4, 6)])]),
             "Созвездия Одетты", ascending=True)
    book.add(Roster(base, [Variation(slot="Яэ Мико", constellations=[0, 1, 2, 6])]),
             "Созвездия Яэ", ascending=True)

    book.save(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

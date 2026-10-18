#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.wriothesley_odette_yae_nicole.rosters
         python -m gi_damage.teams.wriothesley_odette_yae_nicole.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.wriothesley_odette_yae_nicole.builds import (
    BASE_NAME, all_teams, make_team, odette_build)
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

    book.add(Roster(base, [Variation(slot="Ризли", constellations=[1, 2, 6])]),
             "Созвездия Ризли", ascending=True)
    book.add(Roster(base, [Variation(slot="Яэ Мико", constellations=[1, 2, 6])]),
             "Созвездия Яэ", ascending=True)
    book.add(Roster(base, [Variation(slot="Одетта", builds=[
        odette_build(constellation=c) for c in (0, 1, 2, 4, 6)])]),
             "Созвездия Одетты", ascending=True)

    book.save("rosters.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

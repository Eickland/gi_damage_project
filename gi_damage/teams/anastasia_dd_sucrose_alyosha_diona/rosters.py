#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.anastasia_dd_sucrose_alyosha_diona.rosters
         python -m gi_damage.teams.anastasia_dd_sucrose_alyosha_diona.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.teams.anastasia_dd_sucrose_alyosha_diona.builds import all_teams, make_team
from gi_damage.visual.rosters import RosterBook

ANASTASIA_CONSTELLATIONS = (0, 1, 2, 4, 6)


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

    # Созвездия Анастасии меняют баффы всего отряда — сравниваем целые отряды
    book.add([make_team(f"C{c} Анастасия", anastasia_c=c).compute()
              for c in ANASTASIA_CONSTELLATIONS],
             "Созвездия Анастасии", ascending=True)

    book.save("rosters.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.nefer_lauma_columbina_sucrose.rosters
         python -m gi_damage.teams.nefer_lauma_columbina_sucrose.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import compare, hit_details, source_breakdown, team_summary
from gi_damage.data.weapons import *
from gi_damage.teams.nefer_lauma_columbina_sucrose.builds import (
    all_teams, make_team, team_name)


def _section(title: str, teams) -> None:
    print(f"=== {title} ===")
    print(compare([t.compute() for t in teams]))
    print()


def main(argv: list[str]) -> int:
    details = "--details" in argv
    for team in all_teams().values():
        result = team.compute()
        print(team_summary(result))
        if details:
            print(source_breakdown(result))
            print()
            print(hit_details(result))
            print()

    _section("Созвездия Нефер", [make_team(team_name(nefer_c=c), nefer_c=c)
                                 for c in (0, 1, 2, 3, 4, 6)])
    _section("Оружие Нефер", [make_team(f"Нефер: {w.name} R{w.refinement}", nefer_weapon=w)
                              for w in (BLACKMARROW, RELIQUARY_OF_TRUTH_LUNAR.at(1),
                                        RELIQUARY_OF_TRUTH_LUNAR.at(5))])
    _section("Созвездия Лаумы", [make_team(team_name(lauma_c=c), lauma_c=c)
                                 for c in (0, 2, 3, 6)])
    _section("Созвездия Колумбины", [make_team(team_name(columbina_c=c), columbina_c=c)
                                     for c in (0, 1, 2, 4, 6)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

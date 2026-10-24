#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.zibai_linnea_columbina_illuga.rosters
         python -m gi_damage.teams.zibai_linnea_columbina_illuga.rosters --details

Созвездия сравниваются через make_team: у Цзы Бай от созвездия зависит время
ротации, у Линеи — число реакций (C2).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import compare, hit_details, source_breakdown, team_summary
from gi_damage.teams.zibai_linnea_columbina_illuga.builds import (
    BASE_NAME, all_teams, make_team, team_name)


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

    _section("Созвездия Цзы Бай", [make_team(team_name(zibai_c=c), zibai_c=c)
                                   for c in (0, 1, 2, 3, 4, 6)])
    _section("Созвездия Линеи", [make_team(team_name(linnea_c=c), linnea_c=c)
                                 for c in (0, 1, 2, 4, 6)])
    _section("Созвездия Колумбины", [make_team(team_name(columbina_c=c), columbina_c=c)
                                     for c in (0, 1, 2, 4, 6)])
    _section("Созвездия Иллуги", [make_team(team_name(illuga_c=c), illuga_c=c)
                                  for c in (0, 2, 3, 4, 6)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

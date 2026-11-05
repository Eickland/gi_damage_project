#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.cyno_danika_yae_odette.rosters
         python -m gi_damage.teams.cyno_danika_yae_odette.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.teams.cyno_danika_yae_odette.builds import all_teams
from gi_damage.visual.rosters import RosterBook


def main(argv: list[str]) -> int:
    details = "--details" in argv
    book = RosterBook()

    results = []
    for team in all_teams().values():
        result = team.compute()
        results.append(result)
        print(team_summary(result))
        if details:
            print(source_breakdown(result))
            print()
            print(hit_details(result))
            print()

    # C2 Даники меняет удары союзников (стаки), поэтому сравниваем целые отряды
    book.add(results, "Созвездия Даники", ascending=True)

    book.save("rosters.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

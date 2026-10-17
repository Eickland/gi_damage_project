#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.sandrone_yae_alyosha_odette.rosters
         python -m gi_damage.teams.sandrone_yae_alyosha_odette.rosters --details
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import hit_details, source_breakdown, team_summary
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.sandrone_yae_alyosha_odette.builds import (
    BASE_NAME, all_teams, make_team, odette_build, alyosha_build)
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

    book.add(Roster(base, [Variation(slot="Яэ Мико", constellations=[1, 2, 6])]),
             "Созвездия Яэ", ascending=True)
    book.add(Roster(base, [Variation(slot="Яэ Мико",
                                     weapons=[ECHOES.at(5), KAGURA.at(1), WANDERER_SONG_ELECTRO.at(5)])]),
             "Оружие Яэ", ascending=True)
    book.add(Roster(base, [Variation(slot="Сандроне", constellations=[0, 1, 2, 3, 4, 5, 6])]),
             "Созвездия Сандроне", ascending=True)
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

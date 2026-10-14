#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.sandrone_odette_sucrose_alyosha.rosters            (режим по формуле)
         python -m gi_damage.teams.sandrone_odette_sucrose_alyosha.rosters --details   (разбивка по ударам)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.report import (compare, hit_details, source_breakdown,
                                   team_summary)
from gi_damage.core.roster import Roster, Variation
from gi_damage.data.weapons import *
from gi_damage.data.artifacts import *
from gi_damage.teams.sandrone_odette_sucrose_alyosha.builds import all_teams, make_team, alyosha_build, sucrose_build,odette_build,sandrone_build
from gi_damage.core.report import roster_report

from dataclasses import replace

from gi_damage.visual.rosters import RosterBook
    
SHOW_ALL_TEAMS = True

def main(argv: list[str]) -> int:
    details = "--details" in argv
    book = RosterBook() 
    print("Стандарты")

    teams = all_teams()
    results = []
    for team in teams.values():
        result = team.compute()
        results.append(result)
        print(team_summary(result))
        if details:
            print(source_breakdown(result))
            print()
            print(hit_details(result))
            print()

    if SHOW_ALL_TEAMS:
        print("=== Сравнение отрядов ===")
        print(compare(results))
        print()
    # ------------------------------------------------------------------ #
    #  Пример 1: перебор оружия Сандроне                                    #
    # ------------------------------------------------------------------ #

    base = make_team("C0R0 Сандроне, C0R0 Одетта, Сахароза, С2R0 Алеша", 0, TIDAL_SHADOW, 0, SILVER_LIGHT,(DISENCHANTMENT,),(HEART_OF_FORGE,),FAV_LANCE,2,(VIRIDESCENT,),(MILLELITH,))
    
    
    roster = Roster(base, [Variation(slot="Сандроне",
                                     weapons=[TIDAL_SHADOW.at(5),
                                              THOUSAND_SUNS.at(1),
                                              TEASPOON,
                                              FLOWER,
                                              SERPENT_SPINE.at(1),])])
    book.add(roster, "Оружие Сандроне", ascending=True)
    
    roster6 = Roster(base, [Variation(slot="Одетта",
                                     weapons=[SILVER_LIGHT.at(5),
                                              EMBERWELL,
                                              AZURELIGHT.at(1),
                                              FROSTFEATHER.at(1),
                                              FROSTFEATHER.at(3),
                                              FROSTFEATHER.at(5),
                                              FINALE.at(5),
                                              HARBINGER.at(5),
                                              BOUGH.at(1),
                                              BOUGH.at(3),
                                              BOUGH.at(5)])])

    book.add(roster6, "оружие Одетта", ascending=True)
    
    roster7 = Roster(base, [Variation(slot="Алеша",
                                     weapons=[FAV_LANCE,
                                              SYMPHONIST.at(1),
                                              SYMPHONIST.at(2),
                                              SYMPHONIST.at(3),
                                              SYMPHONIST.at(4),
                                              SYMPHONIST.at(5),])])
    book.add(roster7, "Оружие Алеши", ascending=True)

    # ------------------------------------------------------------------ #
    #  Пример 2: созвездия Сандроне × оружие                                #
    # ------------------------------------------------------------------ #

    roster7 = Roster(base, [
        Variation(slot="Сандроне", constellations=[0, 1, 2, 3,4,5, 6]),
    ])
    book.add(roster7, "Созвездия Сандроне", ascending=True)
    
    roster4 = Roster(base, [
        Variation(slot="Одетта", builds=[odette_build(constellation=c,weapon=SILVER_LIGHT) for c in (0, 1, 2,3, 4,5, 6)]),
    ])
    book.add(roster4, "Созвездия Одетты", ascending=True)

    roster9 = Roster(base, [
        Variation(slot="Алеша", builds=[alyosha_build(constellation=c,artifacts=(HEART_OF_FORGE,)) for c in (2, 3, 6)]),
    ])
    book.add(roster9, "Созвездия Алеши", ascending=True)


    roster5 = Roster(base, [
        Variation(slot="Сандроне", artifact_sets=[(DISENCHANTMENT,), (NIGHT_SKY.at(2),AUBADE.at(2)), (SCARLET_PROOF.at(2),DISENCHANTMENT.at(2)),]),
    ])
    book.add(roster5, "Наборы артефактов Сандроне", ascending=True)
            
    book.save("rosters.html")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
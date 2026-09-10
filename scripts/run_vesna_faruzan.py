#!/usr/bin/env python3
"""

Запуск:  python -m scripts.run_vesna_faruzan            (режим по формуле)
         python -m scripts.run_vesna_faruzan --details   (разбивка по ударам)
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
from gi_damage.presets.vesna_faruzan_odette_cmc import all_teams, make_team, faruzan_build, vesna_build,odette_build
from gi_damage.core.report import roster_report

from dataclasses import replace

def keep_viridescent(team):
    """Изумрудная тень обязана быть в отряде.

    Если её не носит Весна — надеваем на Фарузан вместо Инструктора.
    """
    mizuki = team.build("Весна")
    if any(a.name == VIRIDESCENT.name for a in mizuki.artifacts):
        return replace(team, builds=[
        faruzan_build(artifacts=INSTRUCTOR,weapon=FAV_BOW) if b.name == "Фарузан" else b
        for b in team.builds
    ])

    return replace(team, builds=[
        faruzan_build(artifacts=VIRIDESCENT,weapon=FAV_BOW) if b.name == "Фарузан" else b
        for b in team.builds
    ])

    
SHOW_ALL_TEAMS = True

def main(argv: list[str]) -> int:
    details = "--details" in argv

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
    #  Пример 1: перебор оружия Мидзуки                                    #
    # ------------------------------------------------------------------ #

    base = make_team("Весна C0", 0, EMBERWELL, 2, FROSTFEATHER, SCARLET_PROOF, VIRIDESCENT, BREEZEBORNE_BOW.at(1))
    
    
    roster = Roster(base, [Variation(slot="Весна",
                                     weapons=[EMBERWELL.at(5),
                                              LOW_BASE_CRIT_STATSTICK,
                                              HIGH_BASE_CRIT_STATSTICK,
                                              CHRYSALIS.at(1),
                                              CHRYSALIS.at(3),
                                              CHRYSALIS.at(5),
                                              FROSTFEATHER.at(1),
                                              FROSTFEATHER.at(3),
                                              FROSTFEATHER.at(5),
                                              BOUGH.at(1),
                                              BOUGH.at(3),
                                              BOUGH.at(5),
                                              MID_BASE_CRIT_STATSTICK])])
    print("========================")
    print("=== Ростер: оружие Весна (C0) ===")
    print(roster_report(roster.run(), title="оружие Весна (C0)", ascending=True))
    print()
    
    roster6 = Roster(base, [Variation(slot="Одетта",
                                     weapons=[SILVER_LIGHT.at(5),
                                              AZURELIGHT.at(1),
                                              FROSTFEATHER.at(1),
                                              FROSTFEATHER.at(3),
                                              FROSTFEATHER.at(5),
                                              FINALE.at(5),
                                              LOW_BASE_CRIT_STATSTICK,
                                              MID_BASE_CRIT_STATSTICK,
                                              HIGH_BASE_CRIT_STATSTICK,
                                              HARBINGER.at(5),
                                              BOUGH.at(1),
                                              BOUGH.at(3),
                                              BOUGH.at(5)])])
    print("========================")
    print("=== Ростер: оружие Одетта (C0) ===")
    print(roster_report(roster6.run(), title="оружие Одетта (C0)", ascending=True))
    print()

    roster7 = Roster(base, [Variation(slot="Фарузан",
                                     weapons=[FAV_BOW,
                                              BREEZEBORNE_BOW.at(1),
                                              BREEZEBORNE_BOW.at(2),
                                              BREEZEBORNE_BOW.at(3),
                                              BREEZEBORNE_BOW.at(4),
                                              BREEZEBORNE_BOW.at(5),])])
    print("========================")
    print("=== Ростер: оружие Фарузан (C6) ===")
    print(roster_report(roster7.run(), title="оружие Фарузан (C6)", ascending=True))
    print()

    # ------------------------------------------------------------------ #
    #  Пример 2: созвездия Весна × оружие                                #
    # ------------------------------------------------------------------ #

    roster2 = Roster(base, [
        Variation(slot="Весна", constellations=[0, 1, 2, 3,4,5, 6]),
    ],)
    print("========================")
    print("=== Ростер: созвездия Весна ===")
    print(roster_report(roster2.run(), title="созвездия Весна", ascending=True))
    
    roster3 = Roster(base, [
        Variation(slot="Крио ГГ", constellations=[0, 2, 3, 5, 6]),
    ],tweak=keep_viridescent)
    print("========================")
    print("=== Ростер: созвездия Крио ГГ ===")
    print(roster_report(roster3.run(), title="созвездия Крио ГГ", ascending=True))
    
    roster4 = Roster(base, [
        Variation(slot="Одетта", builds=[odette_build(constellation=c) for c in (0, 1, 2,3, 4,5, 6)]),
    ],tweak=keep_viridescent)
    print("========================")
    print("=== Ростер: созвездия Одетта ===")
    print(roster_report(roster4.run(), title="созвездия Одетта", ascending=True))
    
    roster5 = Roster(base, [
        Variation(slot="Весна", artifact_sets=[(VIRIDESCENT,), (EM_2_2_SET,), (SCARLET_PROOF,)]),
    ], tweak=keep_viridescent)
    print("========================")
    print("=== Ростер: наборы артефактов Весны ===")
    print(roster_report(roster5.run(), title="наборы артефактов Весны", ascending=True))        
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
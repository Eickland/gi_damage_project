#!/usr/bin/env python3
"""

Запуск:  python -m scripts.run_mizuki_faruzan            (режим по формуле)
         python -m scripts.run_mizuki_faruzan --details   (разбивка по ударам)
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
from gi_damage.presets.mizuki_faruzan_odette_cmc import all_teams, make_team, faruzan_build, mizuki_build,odette_build
from gi_damage.core.report import roster_report

from dataclasses import replace

def keep_viridescent(team):
    """Изумрудная тень обязана быть в отряде.

    Если её не носит Мидзуки — надеваем на Фарузан вместо Инструктора.
    """
    mizuki = team.build("Мидзуки")
    if any(a.name == VIRIDESCENT.name for a in mizuki.artifacts):
        return replace(team, builds=[
        faruzan_build(artifacts=INSTRUCTOR) if b.name == "Фарузан" else b
        for b in team.builds
    ])

    return replace(team, builds=[
        faruzan_build(artifacts=VIRIDESCENT) if b.name == "Фарузан" else b
        for b in team.builds
    ])

def c6_mizuki_main_stats(team):
    """С C6 корона на МС лучше короны на криты."""
    mizuki = team.build("Мидзуки")
    if mizuki.constellation < 6:
        return team
    stats = dict(mizuki.extra_stats)
    stats[S.CRIT_VALUE] = stats.get(S.CRIT_VALUE, 0) - 0.622   # снять корону на крит
    stats[S.BASE_EM] = stats.get(S.BASE_EM, 0) + 187            # надеть на МС
    return replace(team, builds=[replace(mizuki, extra_stats=stats)
                                 if b.name == "Мидзуки" else b for b in team.builds])
    
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

    base = make_team("Мидзуки C6", 6, SUNNY_MORNING_SLEEP_IN.at(1), 2, FROSTFEATHER, EM_2_2_SET, VIRIDESCENT, BREEZEBORNE_BOW.at(1))
    
    
    roster = Roster(base, [Variation(slot="Мидзуки",
                                     weapons=[WANDERER_SONG.at(5),
                                              SUNNY_MORNING_SLEEP_IN.at(1),
                                              RELIQUARY_OF_TRUTH,
                                              SAC_JADE.at(1),
                                              SAC_JADE.at(5),
                                              STARCALLERS_WATCH,
                                              DAWNING_FROST.at(1),
                                              DAWNING_FROST.at(3),
                                              DAWNING_FROST.at(5),
                                              CEREMONIAL])])
    print("========================")
    print("=== Ростер: оружие Мидзуки (C2) ===")
    print(roster_report(roster.run(), title="оружие Мидзуки (C2)", ascending=True))
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
    #  Пример 2: созвездия Мидзуки × оружие                                #
    # ------------------------------------------------------------------ #

    roster2 = Roster(base, [
        Variation(slot="Мидзуки", constellations=[0, 1, 2, 3, 6]),
    ], tweak=c6_mizuki_main_stats)
    print("========================")
    print("=== Ростер: созвездия Мидзуки ===")
    print(roster_report(roster2.run(), title="созвездия Мидзуки", ascending=True))
    
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
        Variation(slot="Мидзуки", artifact_sets=[(VIRIDESCENT,), (EM_2_2_SET,), (SCARLET_PROOF,)]),
    ], tweak=keep_viridescent)
    print("========================")
    print("=== Ростер: наборы артефактов Мидзуки ===")
    print(roster_report(roster5.run(), title="наборы артефактов Мидзуки", ascending=True))        
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
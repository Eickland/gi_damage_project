#!/usr/bin/env python3
"""
Запуск:  python -m gi_damage.teams.mizuki_vodya_odette_cmc.rosters            (режим по формуле)
         python -m gi_damage.teams.mizuki_vodya_odette_cmc.rosters --details   (разбивка по ударам)
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
from gi_damage.teams.mizuki_vodya_odette_cmc.builds import all_teams, make_team, vodya_build, mizuki_build,odette_build
from gi_damage.core.report import roster_report

from dataclasses import replace

from gi_damage.visual.rosters import RosterBook

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
    
def keep_millelit(team):
    """Миллелит обязан быть в отряде.
    """
    cryo_mc = team.build("Крио ГГ")
    if any(a.name == MILLELITH.name for a in cryo_mc.artifacts):
        return replace(team, builds=[
        vodya_build(artifacts=(MILLELITH.at(2),VOURUKASHA.at(2))) if b.name == "Водяница" else b
        for b in team.builds
    ])
    return replace(team, builds=[
        vodya_build(artifacts=(MILLELITH,)) if b.name == "Водяница" else b
        for b in team.builds
    ])
    
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
    #  Пример 1: перебор оружия Мидзуки                                    #
    # ------------------------------------------------------------------ #

    base = make_team("Мидзуки C2", 2, STARCALLERS_WATCH, 2, SILVER_LIGHT, (GILDED,), (MILLELITH,), MAELSTROM,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2)))
    
    
    roster = Roster(base, [Variation(slot="Мидзуки",
                                     weapons=[WANDERER_SONG.at(5),
                                              SUNNY_MORNING_SLEEP_IN.at(1),
                                              RELIQUARY_OF_TRUTH,
                                              SAC_JADE.at(1),
                                              SAC_JADE.at(5),
                                              STARCALLERS_WATCH,
                                              WINTER.at(1),
                                              WINTER.at(3),
                                              WINTER.at(5),
                                              SACFRAG,
                                              STARSEALED])])
    book.add(roster, "Оружие Мидзуки С6", ascending=True)
    
    roster6 = Roster(base, [Variation(slot="Одетта",
                                     weapons=[SILVER_LIGHT.at(5),
                                              AZURELIGHT.at(1),
                                              FROSTFEATHER.at(1),
                                              FROSTFEATHER.at(3),
                                              FROSTFEATHER.at(5),
                                              FINALE.at(5),
                                              HARBINGER.at(5),
                                              BOUGH.at(1),
                                              BOUGH.at(3),
                                              BOUGH.at(5)])])

    book.add(roster6, "оружие Одетта (C2)", ascending=True)
    
    roster7 = Roster(base, [Variation(slot="Водяница",
                                     weapons=[TTDS_HALF_CATALYSATOR,
                                              MAELSTROM.at(1),
                                              MAELSTROM.at(2),
                                              MAELSTROM.at(3),
                                              MAELSTROM.at(4),
                                              MAELSTROM.at(5),])])
    book.add(roster7, "Оружие Водяница", ascending=True)

    # ------------------------------------------------------------------ #
    #  Пример 2: созвездия Мидзуки × оружие                                #
    # ------------------------------------------------------------------ #

    roster7 = Roster(base, [
        Variation(slot="Мидзуки", constellations=[0, 1, 2, 3, 6]),
    ], tweak=c6_mizuki_main_stats)
    book.add(roster7, "Созвездия Мидзуки", ascending=True)
    
    roster3 = Roster(base, [
        Variation(slot="Крио ГГ", constellations=[0, 2, 3, 5, 6]),
    ])
    book.add(roster3, "Созвездия Крио ГГ", ascending=True)
    
    roster4 = Roster(base, [
        Variation(slot="Одетта", builds=[odette_build(constellation=c) for c in (0, 1, 2,3, 4,5, 6)]),
    ])
    book.add(roster4, "Созвездия Одетта", ascending=True)

    roster9 = Roster(base, [
        Variation(slot="Водяница", builds=[vodya_build(constellation=c,weapon=MAELSTROM) for c in (0, 1, 2,3, 4, 6)]),
    ])
    book.add(roster9, "Созвездия Водяница", ascending=True)


    roster5 = Roster(base, [
        Variation(slot="Мидзуки", artifact_sets=[(VIRIDESCENT,), (NIGHT_SKY.at(2),AUBADE.at(2)), (SCARLET_PROOF,),(GILDED,)]),
    ])
    book.add(roster5, "Наборы артефактов Мидзуки", ascending=True)
 
    
    roster63 = Roster(base, [
        Variation(slot="Крио ГГ", artifact_sets=[(MILLELITH,), (HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2),),]),
    ],tweak=keep_millelit)
    book.add(roster63, "Наборы артефактов Крио ГГ и Водяницы", ascending=True)

            
    book.save("rosters.html")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
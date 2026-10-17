#!/usr/bin/env python3
"""
Поиск по отряду Мидзуки / Фарузан / Крио ГГ / Одетта.

  1. Замены слота «Крио ГГ»: сам Крио ГГ, Ци Ци, Диона.
  2. Порядок инвестиций: что докупать по косту (созвездия, Крио ГГ, сигны).

Запуск:  python -m gi_damage.teams.mizuki_faruzan_cmc_odette.search
Результат: текст в консоли + search.html (карточки с иконками).
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.search import (Candidate, Investable, SignatureWeapon,
                                   find_alternatives, plan_investments)
from gi_damage.data.artifacts import *
from gi_damage.data.weapons import *
from gi_damage.teams.vesna_vodya_odette_cmc.builds import (
    cryo_mc_build, make_team, vesna_build, odette_build)
from gi_damage.teams.mizuki_faruzan_diona_odette.builds import diona_build
from gi_damage.teams.mizuki_faruzan_qiqi_odette.builds import qiqi_build
from gi_damage.teams.mizuki_faruzan_qiqi_odette.builds import faruzan_build
from gi_damage.teams.mizuki_vodya_odette_cmc.builds import vodya_build
from gi_damage.visual import SearchBook



# --------------------------------------------------------------------------- #
#  1. Замены слота                                                            #
# --------------------------------------------------------------------------- #
def alternatives(book: SearchBook) -> None:
    base = make_team("База", 0, EMBERWELL.at(5), 0, SILVER_LIGHT,
                         SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0,4, 
                         (HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2)))

    candidates = [
        Candidate("Крио ГГ", lambda c: cryo_mc_build(c, MILLELITH),
                  constellations=(0, 4, 6), weapons=[EXAIPHANES],
                  artifact_sets=[(MILLELITH,),
                                 (HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2))]),
        Candidate("Ци Ци", lambda c: qiqi_build(c, MILLELITH),
                  constellations=(0, 6), weapons=[FAV_SWORD],
                  artifact_sets=[(MILLELITH,)]),
        Candidate("Диона", lambda c: diona_build(c, MILLELITH),
                  constellations=(0, 6),
                  weapons=[FAV_BOW, BREEZEBORNE_BOW.at(1)],
                  artifact_sets=[(MILLELITH,)]),
    ]
    report = find_alternatives(base, "Крио ГГ", candidates)
    book.add_alternatives(report, "Замены слота «Крио ГГ» (Мидзуки C2)")


# --------------------------------------------------------------------------- #
#  2. Порядок инвестиций                                                      #
# --------------------------------------------------------------------------- #
def investments(book: SearchBook, budget: int = 36) -> None:
    # База: всё доступное. В слоте Крио ГГ пока стоит бесплатная Ци Ци.
    baseline = make_team("База", 0, BOUGH.at(3), 0, SILVER_LIGHT,
                         SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0,4, 
                         (HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2)))
    
    baseline = replace(baseline, builds=[
        faruzan_build(FAV_BOW,) if b.name == "Водяница" else b
        for b in baseline.builds])
    baseline = replace(baseline, builds=[
        diona_build(6,HEART_OF_FORGE) if b.name == "Одетта" else b
        for b in baseline.builds])
 
    investables = [
        Investable("Весна", "Весна",
                   lambda c: vesna_build(c, BOUGH.at(3),SCARLET_PROOF),
                   max_constellation=6, owned=True),
        # C0 уже есть, платные только созвездия
        Investable("Одетта", "Диона",
                   lambda c: odette_build(c, SILVER_LIGHT),
                   max_constellation=6, owned=False),
        # C0 тоже стоит кост; пока не куплен — в слоте «Ци Ци»
        Investable("Водяница", "Фарузан",
                   lambda c: vodya_build(c,TTDS_HALF_CATALYSATOR, (MILLELITH,)),
                   max_constellation=6, owned=False),
    ]
    weapons = [
        SignatureWeapon("Весна", CHRYSALIS, 5, character="Весна"),
        SignatureWeapon("Одетта", FROSTFEATHER, 5, character="Одетта"),
        SignatureWeapon("Водяница", MAELSTROM, 5, character="Водяница"),
    ]
    plan = plan_investments(baseline, investables, weapons, budget=budget,)
    book.add_plan(plan, f"Порядок инвестиций (до {budget} костов)",
                  notes=["Кост = C0 персонажа, любое созвездие, R1 сигны и каждое пробуждение.",
                         "Если на косте меняется несколько позиций — лучший вариант не "
                         "достраивается из лучшего предыдущего."])


SEARCH_ALTERNATIVE = False
INVEST_ORDER = True

def main(argv: list[str]) -> int:
    book = SearchBook()
    if SEARCH_ALTERNATIVE:
        alternatives(book)
    if INVEST_ORDER:
        investments(book)
    print(f"HTML: {book.save('search.html').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
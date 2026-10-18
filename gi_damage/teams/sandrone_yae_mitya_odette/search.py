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
from gi_damage.teams.sandrone_yae_mitya_odette.builds import (
    sandrone_build, make_team, yae_build, odette_build,mitya_build)
from gi_damage.teams.mizuki_faruzan_cmc_odette.rosters import c6_mizuki_main_stats
from gi_damage.teams.mizuki_faruzan_diona_odette.builds import diona_build
from gi_damage.teams.mizuki_faruzan_qiqi_odette.builds import qiqi_build
from gi_damage.teams.sandrone_odette_mitya_alyosha.builds import alyosha_build
from gi_damage.teams.mizuki_vodya_odette_cmc.builds import vodya_build
from gi_damage.visual import SearchBook



# --------------------------------------------------------------------------- #
#  1. Замены слота                                                            #
# --------------------------------------------------------------------------- #
def alternatives(book: SearchBook) -> None:
    base = make_team("База", 0, ATONEMENT, 0, SILVER_LIGHT,1,
                         ECHOES,0,TTDS_FULL_CATALYSATOR,(DISENCHANTMENT,),(HEART_OF_FORGE,), 
                         (DISENCHANTMENT,),(MILLELITH,))

    candidates = [
        Candidate("Одетта", lambda c: odette_build(c, SILVER_LIGHT,(HEART_OF_FORGE,)),
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
    report = find_alternatives(base, "Одетта", candidates)
    book.add_alternatives(report, "Замены слота «Одетта»")


# --------------------------------------------------------------------------- #
#  2. Порядок инвестиций                                                      #
# --------------------------------------------------------------------------- #
def investments(book: SearchBook, budget: int = 40) -> None:
    # База: всё доступное. В слоте Крио ГГ пока стоит бесплатная Ци Ци.
    baseline = make_team("База", 0, ATONEMENT, 0, SILVER_LIGHT,1,
                         ECHOES,0,TTDS_FULL_CATALYSATOR,(DISENCHANTMENT,),(DISENCHANTMENT,), 
                         (HEART_OF_FORGE,),(MILLELITH,))

    baseline = replace(baseline, builds=[
        alyosha_build(6,FAV_LANCE,(HEART_OF_FORGE,)) if b.name == "Яэ Мико" else b
        for b in baseline.builds])
    baseline = replace(baseline, builds=[
        diona_build(6,NOBLESSE) if b.name == "Одетта" else b
        for b in baseline.builds])
    baseline = replace(baseline, builds=[
        qiqi_build(6,MILLELITH) if b.name == "Митя" else b
        for b in baseline.builds])
 
    investables = [
        Investable("Сандроне", "Сандроне",
                   lambda c: sandrone_build(c, ATONEMENT,(DISENCHANTMENT,)),
                   max_constellation=6, owned=True),
        # C0 уже есть, платные только созвездия
        Investable("Одетта", "Диона",
                   lambda c: odette_build(c, SILVER_LIGHT,(DISENCHANTMENT,)),
                   max_constellation=6, owned=False),
        # C0 тоже стоит кост; пока не куплен — в слоте «Ци Ци»
        Investable("Яэ Мико", "Алеша",
                   lambda c: yae_build(c,ECHOES, (HEART_OF_FORGE,)),
                   max_constellation=6, owned=False),
        Investable("Митя", "Ци Ци",
                   lambda c: mitya_build(c,TTDS_FULL_CATALYSATOR, (MILLELITH,)),
                   max_constellation=6, owned=False),
    ]
    weapons = [
        SignatureWeapon("Одетта", FROSTFEATHER, 5, character="Одетта"),
        SignatureWeapon("Сандроне", TEASPOON, 5, character="Сандроне"),
        SignatureWeapon("Яэ Мико", KAGURA, 5, character="Яэ Мико"),
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
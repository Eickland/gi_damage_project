#!/usr/bin/env python3
"""
Поиск по отряду Мидзуки / Фарузан / Крио ГГ / Одетта.

  1. Замены слота «Крио ГГ»: сам Крио ГГ, Ци Ци, Диона.
  2. Порядок инвестиций: что докупать по косту (созвездия, Крио ГГ, сигны).

Запуск:  python -m gi_damage.teams.zibai_linnea_columbina_illuga.search
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
from gi_damage.teams.zibai_linnea_columbina_illuga.builds import (
    zibai_build, make_team, columbina_build,linnea_build,illuga_build)
from gi_damage.teams.mizuki_faruzan_cmc_odette.rosters import c6_mizuki_main_stats
from gi_damage.teams.mizuki_faruzan_diona_odette.builds import diona_build
from gi_damage.teams.mizuki_faruzan_qiqi_odette.builds import qiqi_build
from gi_damage.teams.sandrone_odette_mitya_alyosha.builds import alyosha_build
from gi_damage.teams.sandrone_odette_sucrose_alyosha.builds import sucrose_build
from gi_damage.visual import SearchBook



# --------------------------------------------------------------------------- #
#  1. Замены слота                                                            #
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
#  2. Порядок инвестиций                                                      #
# --------------------------------------------------------------------------- #
def investments(book: SearchBook, budget: int = 40) -> None:
    # База: всё доступное. В слоте Крио ГГ пока стоит бесплатная Ци Ци.
    baseline = make_team("База", 0, 0,0,6,HARBINGER,COVENANT_FROST_SNOW,PROTOTYPE_AMBER, DRAGONS_BANE,
                         (NIGHT_SKY,),(AUBADE,),(AUBADE,),(SERENADE,))
 
    investables = [
        Investable("Цзы Бай", "Цзы Бай",
                   lambda c: zibai_build(c, HARBINGER,(NIGHT_SKY,)),
                   max_constellation=6, owned=True),
        # C0 уже есть, платные только созвездия
        Investable("Линея", "Линея",
                   lambda c: linnea_build(c, COVENANT_FROST_SNOW,(AUBADE,)),
                   max_constellation=6, owned=True),
        Investable("Колумбина", "Колумбина",
                   lambda c: columbina_build(c,PROTOTYPE_AMBER, (AUBADE,)),
                   max_constellation=6, owned=True),
    ]
    weapons = [
        SignatureWeapon("Цзы Бай", MOONSHARD, 5, character="Цзы Бай"),
        SignatureWeapon("Колумбина", NOCTURNE, 5, character="Колумбина"),
        SignatureWeapon("Линея", GOLDEN_OATH, 5, character="Линея"),
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
    if INVEST_ORDER:
        investments(book)
    print(f"HTML: {book.save('search.html').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
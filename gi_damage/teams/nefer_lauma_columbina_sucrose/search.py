#!/usr/bin/env python3
"""
Поиск по отряду Нефер / Лаума / Колумбина / Сахароза: порядок инвестиций.

Запуск:  python -m gi_damage.teams.nefer_lauma_columbina_sucrose.search
Результат: текст в консоли + search.html (карточки с иконками).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.search import Investable, SignatureWeapon, plan_investments
from gi_damage.data.artifacts import *
from gi_damage.data.weapons import *
from gi_damage.teams.nefer_lauma_columbina_sucrose.builds import (
    make_team, nefer_build, lauma_build, columbina_build)
from gi_damage.visual import SearchBook


def investments(book: SearchBook, budget: int = 40) -> None:
    # База: C0 всех, безсигнатурное оружие. Сахароза C6 — бесплатна.
    baseline = make_team("База")

    investables = [
        Investable("Нефер", "Нефер",
                   lambda c: nefer_build(c, BLACKMARROW, (NIGHT_SKY,)),
                   max_constellation=6, owned=True),
        Investable("Лаума", "Лаума",
                   lambda c: lauma_build(c, SPINDLELUTE, (DEEPWOOD,)),
                   max_constellation=6, owned=True),
        Investable("Колумбина", "Колумбина",
                   lambda c: columbina_build(c, PROTOTYPE_AMBER, (SERENADE,)),
                   max_constellation=6, owned=True),
    ]
    weapons = [
        SignatureWeapon("Нефер", RELIQUARY_OF_TRUTH_LUNAR, 5, character="Нефер"),
        SignatureWeapon("Колумбина", NOCTURNE, 5, character="Колумбина"),
        SignatureWeapon("Лаума", NIGHTWEAVER_LUNAR, 5, character="Лаума"),
    ]
    plan = plan_investments(baseline, investables, weapons, budget=budget)
    book.add_plan(plan, f"Порядок инвестиций (до {budget} костов)",
                  notes=["Кост = C0 персонажа, любое созвездие, R1 сигны и каждое пробуждение.",
                         "Если на косте меняется несколько позиций — лучший вариант не "
                         "достраивается из лучшего предыдущего."])


def main(argv: list[str]) -> int:
    book = SearchBook()
    investments(book)
    print(f"HTML: {book.save('search.html').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

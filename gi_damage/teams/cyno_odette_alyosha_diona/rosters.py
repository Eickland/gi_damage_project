#!/usr/bin/env python3
"""
Ростеры отряда cyno_odette_alyosha_diona: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py);
плюс сравнение главных статов (текстом).

Запуск:  python -m gi_damage.teams.cyno_odette_alyosha_diona.rosters
         python -m gi_damage.teams.cyno_odette_alyosha_diona.rosters --details
         python -m gi_damage.teams.cyno_odette_alyosha_diona.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.cyno_odette_alyosha_diona import builds
from gi_damage.visual.standard_rosters import run_standard, print_main_stats


def extra(book, base) -> None:
    print_main_stats(builds, "Сайно", "cyno_main_stats", (("АТК/АТК/крит", builds.CYNO_MAIN_ATK), ("МС/АТК/крит", builds.CYNO_MAIN_EM), ("АТК/электро/крит", builds.CYNO_MAIN_ELECTRO)))


def main(argv: list[str]) -> int:
    return run_standard(builds, argv, extra=extra)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

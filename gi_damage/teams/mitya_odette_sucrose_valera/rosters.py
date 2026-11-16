#!/usr/bin/env python3
"""
Ростеры отряда mitya_odette_sucrose_valera: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py);
плюс сравнение главных статов (текстом).

Запуск:  python -m gi_damage.teams.mitya_odette_sucrose_valera.rosters
         python -m gi_damage.teams.mitya_odette_sucrose_valera.rosters --details
         python -m gi_damage.teams.mitya_odette_sucrose_valera.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.mitya_odette_sucrose_valera import builds
from gi_damage.visual.standard_rosters import run_standard, print_main_stats


def extra(book, base) -> None:
    print_main_stats(builds, "Митя", "mitya_main_stats", (("МС/МС/крит", builds.MAIN_EM), ("МС/электро/крит", builds.MAIN_EM_ELECTRO)))


def main(argv: list[str]) -> int:
    return run_standard(builds, argv, extra=extra)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

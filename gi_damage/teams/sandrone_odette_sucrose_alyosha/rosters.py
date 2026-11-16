#!/usr/bin/env python3
"""
Ростеры отряда sandrone_odette_sucrose_alyosha: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py);
плюс ростер замен Сахарозы (Даника / Анастасия).

Запуск:  python -m gi_damage.teams.sandrone_odette_sucrose_alyosha.rosters
         python -m gi_damage.teams.sandrone_odette_sucrose_alyosha.rosters --details
         python -m gi_damage.teams.sandrone_odette_sucrose_alyosha.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.sandrone_odette_sucrose_alyosha import builds
from gi_damage.visual.standard_rosters import run_standard


def extra(book, base) -> None:
    """Замена Сахарозы на Данику / Анастасию (обе C0)."""
    book.add_swaps([t.compute() for t in builds.swap_teams().values()],
                   "Замена Сахарозы: Даника / Анастасия (C0)")


def main(argv: list[str]) -> int:
    return run_standard(builds, argv, extra=extra)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

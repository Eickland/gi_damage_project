#!/usr/bin/env python3
"""
Ростеры отряда mitya_odette_danika_valera: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py).

Запуск:  python -m gi_damage.teams.mitya_odette_danika_valera.rosters
         python -m gi_damage.teams.mitya_odette_danika_valera.rosters --details
         python -m gi_damage.teams.mitya_odette_danika_valera.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.mitya_odette_danika_valera import builds
from gi_damage.visual.standard_rosters import run_standard


def main(argv: list[str]) -> int:
    return run_standard(builds, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

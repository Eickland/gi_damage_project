#!/usr/bin/env python3
"""
Ростеры отряда sandrone_odette_mitya_danika: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py).

Запуск:  python -m gi_damage.teams.sandrone_odette_mitya_danika.rosters
         python -m gi_damage.teams.sandrone_odette_mitya_danika.rosters --details
         python -m gi_damage.teams.sandrone_odette_mitya_danika.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.sandrone_odette_mitya_danika import builds
from gi_damage.visual.standard_rosters import run_standard


def main(argv: list[str]) -> int:
    return run_standard(builds, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

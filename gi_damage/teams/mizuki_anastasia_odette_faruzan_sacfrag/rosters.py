#!/usr/bin/env python3
"""
Ростеры отряда mizuki_anastasia_odette_faruzan_sacfrag: созвездия, оружие и артефакты каждого
персонажа (gi_damage/visual/standard_rosters.py).

Запуск:  python -m gi_damage.teams.mizuki_anastasia_odette_faruzan_sacfrag.rosters
         python -m gi_damage.teams.mizuki_anastasia_odette_faruzan_sacfrag.rosters --details
         python -m gi_damage.teams.mizuki_anastasia_odette_faruzan_sacfrag.rosters --out файл.html
HTML по умолчанию — rosters.html в папке отряда.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.teams.mizuki_anastasia_odette_faruzan_sacfrag import builds
from gi_damage.visual.standard_rosters import run_standard


#: Не строить: оружие Мидзуки (в отряде всегда Церемон)
SKIP = {("Мидзуки", "weapon")}


def main(argv: list[str]) -> int:
    return run_standard(builds, argv, skip=SKIP)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

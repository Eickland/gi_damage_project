#!/usr/bin/env python3
"""
Ростеры отряда Цзы Бай / Линея / Колумбина / Иллуги.

Запуск:  python -m gi_damage.teams.zibai_linnea_columbina_illuga.rosters
         python -m gi_damage.teams.zibai_linnea_columbina_illuga.rosters --details

Стандартные ростеры (gi_damage/visual/standard_rosters.py) собираются на
Линее C0. Созвездия Линеи меняют число реакций (C2), поэтому в стандартном
ростере созвездий их нет. Вместо него два отдельных ростера:
  * «Созвездия Линеи (C0–C1)» — от базы C0;
  * «Созвездия Линеи от C2» — база C2 (с её числом реакций), от неё C3–C6.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gi_damage.core.engine import Team
from gi_damage.teams.zibai_linnea_columbina_illuga import builds
from gi_damage.visual.rosters import RosterBook
from gi_damage.visual.standard_rosters import run_standard

#: стандартный ростер созвездий Линеи не строим (меняются реакции)
SKIP = {("Линея", "c")}
#: в ростерах на базе C0 Линея не выше C1
LINNEA_MAX_C = 1


def _linnea(c: int):
    return builds.make_team(f"C{c}", linnea_c=c).compute()


def extra(book: RosterBook, base: Team) -> None:
    book.add([_linnea(c) for c in range(LINNEA_MAX_C + 1)],
             "Созвездия — Линея (C0–C1)", base=0,
             notes=[f"Линея ограничена C{LINNEA_MAX_C}: с C2 меняется число реакций"])
    book.add([_linnea(c) for c in range(2, 7)],
             "Созвездия — Линея от C2", base=0,
             notes=["база — отряд с C2 Линеи (реакции C2); % от базы — к нему"])


def main(argv: list[str]) -> int:
    return run_standard(builds, argv, extra=extra, skip=SKIP)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

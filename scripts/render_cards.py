#!/usr/bin/env python3
"""Карточки отрядов с иконками (HTML, по желанию PNG).

    python -m scripts.render_cards                                  # отряд по умолчанию
    python -m scripts.render_cards --team mizuki_faruzan_cmc_odette --columns 2
    python -m scripts.render_cards --png                            # + PNG (нужен playwright)

Текстовый вывод (python -m gi_damage.teams.<отряд>.rosters) работает как раньше.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.visual import IconStore, save_cards, save_png


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--team", default="mizuki_sucrose_cmc_odette",
                    help="папка в gi_damage/teams с модулем builds.py")
    ap.add_argument("--out", default="cards.html")
    ap.add_argument("--columns", type=int, default=2)
    ap.add_argument("--png", action="store_true", help="также сохранить PNG")
    args = ap.parse_args()

    builds = importlib.import_module(f"gi_damage.teams.{args.team}.builds")
    results = [t.compute() for t in builds.all_teams().values()]

    store = IconStore()
    for kind, getter in (
        ("characters", lambda s: s.character),
        ("weapons", lambda s: s.weapon.rsplit(" R", 1)[0]),
        ("artifacts", None),
    ):
        names = set()
        for r in results:
            for s in r.setup.values():
                if kind == "artifacts":
                    names.update(a for a in s.artifacts.split("/") if a)
                else:
                    names.add(getter(s)) # type: ignore
        miss = store.missing(kind, names)
        if miss:
            print(f"нет иконок ({kind}): {', '.join(miss)}")

    path = save_cards(results, args.out, title=args.team, columns=args.columns,
                      store=store)
    print(f"HTML: {path.resolve()}")
    if args.png:
        print(f"PNG:  {save_png(path, Path(args.out).with_suffix('.png')).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""
Сравнение обычного комбо Сайно (sc_combo: QE (N2 CA N4 E)×3, 15 с)
с укороченным (sc_short_combo: QE (N2 CA N4 E)×2, 10.5 с) во всех отрядах Сайно.

Запуск:  python -m scripts.compare_cyno_short
"""
from __future__ import annotations

import importlib
import inspect
from contextlib import contextmanager

from gi_damage.data.characters.cyno import CYNO_COMBO_DICT, CYNO_SC_SHORT_TIME

TEAMS = (
    "cyno_anastasia_danika_odette",
    "cyno_danika_yae_odette",
    "cyno_odette_alyosha_diona",
    "cyno_odette_yae_alyosha",
    "cyno_odette_yae_diona",
    "cyno_yae_danika_anastasia",
    "cyno_yae_odette_valera",
)
CONSTELLATIONS = (1, 2, 6)


@contextmanager
def short_cyno(mod):
    """Временно подменить в модуле отряда комбо и время Сайно."""
    saved = {k: getattr(mod, k) for k in ("CYNO", "CYNO_COMBO_DICT") if hasattr(mod, k)}
    times = dict(mod.TIMES)
    mod.TIMES["Сайно"] = CYNO_SC_SHORT_TIME
    short = CYNO_COMBO_DICT["sc_short_combo"]
    if hasattr(mod, "CYNO"):
        mod.CYNO = short
    mod.CYNO_COMBO_DICT = {**CYNO_COMBO_DICT, "sc_combo": short}
    try:
        yield
    finally:
        mod.TIMES.clear(); mod.TIMES.update(times)
        for k, v in saved.items():
            setattr(mod, k, v)


def main() -> int:
    for team_mod in TEAMS:
        mod = importlib.import_module(f"gi_damage.teams.{team_mod}.builds")
        name = next(iter(mod.all_teams()))
        params = inspect.signature(mod.make_team).parameters
        print(f"\n=== {name} ===")
        print(f"{'Сайно':>6} | {'обычное ДПС':>12} | {'короткое ДПС':>12} | {'разница':>8} | ротация")
        for c in CONSTELLATIONS:
            kw = {"cyno_c": c} if "cyno_c" in params else {}
            base = mod.make_team("base", **kw).compute()
            with short_cyno(mod):
                short = mod.make_team("short", **kw).compute()
            d = short.dps / base.dps - 1
            print(f"{'C' + str(c):>6} | {base.dps:12,.0f} | {short.dps:12,.0f} | {d:+8.2%} | "
                  f"{base.rotation_time:.2f} → {short.rotation_time:.2f} с")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Сравнение обычного комбо Сандроне (sandrone_sc_combo) с укороченным
(sandrone_c0_sc_short_combo, только C0: −1 заряженная атака, −4 с) в отрядах с 3 крио.

Запуск:  python -m scripts.compare_sandrone_short
"""
from __future__ import annotations

import importlib
from contextlib import contextmanager

from gi_damage.data.characters.sandrone import SANDRONE_COMBO_DICT, SANDRONE_ONE_CA_TIME

TEAMS = (
    "sandrone_anastasia_danika_odette",
    "sandrone_odette_qiqi_alyosha",
    "sandrone_odette_yae_anastasia",
)
CONSTELLATIONS = (0,)   # укороченная ротация возможна только на C0


@contextmanager
def short_sandrone(mod):
    """Временно подменить в модуле отряда комбо и время Сандроне."""
    saved = dict(vars(mod))
    times = dict(mod.TIMES)
    mod.TIMES["Сандроне"] = times["Сандроне"] - SANDRONE_ONE_CA_TIME
    short = SANDRONE_COMBO_DICT["sandrone_c0_sc_short_combo"]
    if hasattr(mod, "SANDRONE"):
        mod.SANDRONE = short
    mod.SANDRONE_COMBO_DICT = {**SANDRONE_COMBO_DICT, "sandrone_sc_combo": short}
    try:
        yield
    finally:
        mod.TIMES.clear(); mod.TIMES.update(times)
        for k in ("SANDRONE", "SANDRONE_COMBO_DICT"):
            if k in saved:
                setattr(mod, k, saved[k])


def main() -> int:
    for team_mod in TEAMS:
        mod = importlib.import_module(f"gi_damage.teams.{team_mod}.builds")
        print(f"\n=== {mod.BASE_NAME} ===")
        print(f"{'Сандроне':>9} | {'обычное ДПС':>12} | {'без 1 CA ДПС':>12} | {'разница':>8} | ротация")
        for c in CONSTELLATIONS:
            base = mod.make_team("base", sandrone_c=c).compute()
            with short_sandrone(mod):
                short = mod.make_team("short", sandrone_c=c).compute()
            d = short.dps / base.dps - 1
            print(f"{'C' + str(c):>9} | {base.dps:12,.0f} | {short.dps:12,.0f} | {d:+8.2%} | "
                  f"{base.rotation_time:.2f} → {short.rotation_time:.2f} с")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

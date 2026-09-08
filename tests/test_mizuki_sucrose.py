"""
Сверка расчёта с исходной таблицей Excel (лист «Мидзуки Сахароза»).

Запуск:  python -m pytest tests -q
     или python tests/test_mizuki_sucrose.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.engine import StatResolver
from gi_damage.core.formulas import base_increase, ssw_multiplier
from gi_damage.data.tags import INST, OFF, ON
from gi_damage.presets.mizuki_sucrose_00 import (EXCEL_VALUES, VORTEX_EVENTS,
                                              all_teams)

TOL = 1e-6   # относительная точность


def _split(result):
    vortex = sum(v for ch in result.characters.values()
                 for name, v in ch.reaction_breakdown.items()
                 if name in VORTEX_EVENTS)
    return result.dpr - vortex, vortex


def _close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(b))


# --------------------------------------------------------------------------- #
def test_all_blocks_match_excel():
    for name, team in all_teams(excel_compat=True).items():
        result = team.compute()
        no_vortex, vortex = _split(result)
        ref = EXCEL_VALUES[name]
        assert _close(no_vortex, ref["dpr_no_vortex"]), f"{name}: DPR {no_vortex} != {ref['dpr_no_vortex']}"
        assert _close(vortex, ref["vortex"]), f"{name}: вихрь {vortex} != {ref['vortex']}"
        assert _close(no_vortex / result.rotation_time, ref["dps"]), f"{name}: DPS"


# --------------------------------------------------------------------------- #
#  Промежуточные величины блока 2 (Мидзуки C1, Песнь странника R5)             #
# --------------------------------------------------------------------------- #
BLOCK2 = "Блок 2 — Мидзуки C1 (Песнь странника R5)"

STATES = {"on": frozenset({ON}), "on+i": frozenset({ON, INST}),
          "off": frozenset({OFF}), "off+i": frozenset({OFF, INST})}

EXPECTED_EM = {
    ("Мидзуки", "on"): 1043.9, ("Мидзуки", "on+i"): 1385.1000000000001,
    ("Крио ГГ", "on"): 375.0, ("Крио ГГ", "on+i"): 754.2,
    ("Крио ГГ", "off"): 349.9, ("Крио ГГ", "off+i"): 621.1,
    ("Одетта", "on"): 408.0, ("Одетта", "on+i"): 578.0,
    ("Одетта", "off"): 382.9, ("Одетта", "off+i"): 654.1,
    ("Сахароза", "on"): 1046.0, ("Сахароза", "off"): 1020.9,
}

EXPECTED_EMM = {
    ("Мидзуки", "on"): 5.841207420035151,
    ("Мидзуки", "on+i"): 6.5078011120631585,
    ("Крио ГГ", "on"): 3.687315789473684,
    ("Крио ГГ", "on+i"): 4.529051702853824,
    ("Крио ГГ", "off"): 4.1904172101557515,
    ("Крио ГГ", "off+i"): 5.015528028173287,
    ("Одетта", "on+i"): 4.168726920093095,
    ("Одетта", "off"): 3.5499879639493894,
    ("Одетта", "off+i"): 4.358405894274896,
    ("Сахароза", "off"): 5.56288893515012,
    ("Сахароза", "off+i"): 5.748672335150121,
}

EXPECTED_ATK = {"Мидзуки": 1618.75, "Крио ГГ": 2484.76,
                "Одетта": 2923.025, "Сахароза": 1192.4}


def _resolver():
    return StatResolver(all_teams(excel_compat=True)[BLOCK2].builds, 4)


def test_atk():
    r = _resolver()
    for name, expected in EXPECTED_ATK.items():
        assert _close(r.stats(name, STATES["on"]).atk, expected), name


def test_em_by_state():
    r = _resolver()
    for (name, st), expected in EXPECTED_EM.items():
        got = r.stats(name, STATES[st]).em
        assert _close(got, expected), f"{name} {st}: {got} != {expected}"


def test_stellar_swirl_multiplier():
    """Строки «EMM» таблицы = (1 + 6МС/(МС+2000) + бонус) × (1 + базовый бонус)."""
    r = _resolver()
    tags = ("anemo", "stellar_swirl", "reaction")
    for (name, st), expected in EXPECTED_EMM.items():
        s = r.stats(name, STATES[st])
        got = ssw_multiplier(s, *tags) * base_increase(s, *tags)
        assert _close(got, expected), f"{name} {st}: {got} != {expected}"


def test_block2_source_totals():
    """Строки «Total Elemental DMG» и «Total SSW DMG» блока 2."""
    result = all_teams(excel_compat=True)[BLOCK2].compute()
    by = {n: ch.by_source() for n, ch in result.characters.items()}

    mizuki_elemental = sum(v for k, v in by["Мидзуки"].items()
                           if "рассеивание" not in k)
    mizuki_ssw = sum(v for k, v in by["Мидзуки"].items() if "рассеивание" in k)
    assert _close(mizuki_elemental, 134296.97931137917)
    assert _close(mizuki_ssw, 940606.2244426513)

    assert _close(by["Крио ГГ"]["Навык (АТК)"], 21932.7542830656)
    assert _close(sum(v for k, v in by["Крио ГГ"].items() if "SSW" in k),
                  528854.1089734581)

    assert _close(by["Одетта"]["Навык (АТК)"], 48405.445327917776)
    assert _close(sum(v for k, v in by["Одетта"].items() if "SSW" in k),
                  608355.2006209188)


def test_excel_compat_flag_changes_result():
    """Без режима совместимости числа должны отличаться (двойной учёт убран)."""
    a = all_teams(excel_compat=True)[BLOCK2].compute().dpr
    b = all_teams(excel_compat=False)[BLOCK2].compute().dpr
    assert not _close(a, b)


def test_resistance_model_reproduces_table_multipliers():
    """Множители сопротивления из таблицы должны выводиться из базового RES."""
    from gi_damage.core.formulas import (inverse_resistance_multiplier,
                                         resistance_multiplier)
    # анемо: +10% базовых, C2 снимает 20%
    assert _close(resistance_multiplier(0.10), 0.90)
    assert _close(resistance_multiplier(0.10 - 0.20), 1.05)
    # крио: +10% базовых, -40% Изумрудная тень, C2 снимает ещё 20%
    assert _close(resistance_multiplier(0.10 - 0.40), 1.15)
    assert _close(resistance_multiplier(0.10 - 0.40 - 0.20), 1.25)
    # обратное преобразование
    for mult in (0.90, 1.05, 1.15, 1.25, 0.20):
        assert _close(resistance_multiplier(inverse_resistance_multiplier(mult)), mult)


def test_c2_resistance_shred_is_state_dependent():
    """Снижение сопротивления от C2 работает только внутри окна Dreamdrifter."""
    from gi_damage.core.engine import StatResolver
    from gi_damage.data.tags import DREAM

    team = all_teams(excel_compat=False)["Блок 4 — Мидзуки C2 (Песнь странника R5)"]
    r = StatResolver(team.builds, 4)

    inside = r.stats("Крио ГГ", frozenset({OFF, DREAM}))
    outside = r.stats("Крио ГГ", frozenset({OFF}))

    # внутри окна: 40% (Изумрудная тень) + 20% (C2); снаружи только 40%
    assert _close(inside.res_reduction("cryo"), 0.60)
    assert _close(outside.res_reduction("cryo"), 0.40)
    assert _close(team.enemy.res_multiplier("cryo", inside.res_reduction("cryo")), 1.25)
    assert _close(team.enemy.res_multiplier("cryo", outside.res_reduction("cryo")), 1.15)

    # анемо шредится только внутри окна
    assert _close(team.enemy.res_multiplier("anemo", inside.res_reduction("anemo")), 1.05)
    assert _close(team.enemy.res_multiplier("anemo", outside.res_reduction("anemo")), 0.90)


def test_c2_dmg_bonus_goes_to_cryo_not_anemo():
    """Бонус C2 даётся крио-персонажам, а не самой Мидзуки (она анемо)."""
    from gi_damage.core.engine import StatResolver
    from gi_damage.data.tags import DREAM

    team = all_teams(excel_compat=False)["Блок 4 — Мидзуки C2 (Песнь странника R5)"]
    r = StatResolver(team.builds, 4)
    odette = r.stats("Одетта", frozenset({OFF, DREAM, INST}))
    mizuki = r.stats("Мидзуки", frozenset({ON, DREAM, INST}))

    assert _close(odette.dmg_bonus("cryo"), 0.0004 * 1385.1000000000001)
    assert _close(mizuki.dmg_bonus("anemo"), 0.32)   # только бонус оружия


def test_roster_runs():
    from gi_damage.core.roster import Roster, Variation
    from gi_damage.data.weapons import SUNNY_MORNING_SLEEP_IN, WANDERER_SONG
    team = all_teams(excel_compat=True)[BLOCK2]
    roster = Roster(team, [Variation(slot="Мидзуки",
                                     weapons=[WANDERER_SONG.at(5),
                                              SUNNY_MORNING_SLEEP_IN.at(1)])])
    results = roster.run()
    assert len(results) == 2
    assert all(r.dpr > 0 for r in results)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\nПровалено тестов: {failures}")
    raise SystemExit(1 if failures else 0)

"""
Ризли — крио, катализатор. ДД звёздного проводника (всегда Radiance:
Stellar-Conduct). C1 — базовая линия.

Базовое комбо: 3 × (N5 CA) в Chilling Penalty, 10.1 с.
    Все обычные атаки усилены Chilling Penalty: 170.31% урона обычной атаки.
    3-й и 5-й удары — звёздный проводник: 60% / 80% исходного урона
    (C2: 90% / 120%). Заряженная (Luster: Vaulting Fist) — звёздный
    проводник, 100% (C2: 150%). 1-й, 2-й, 4-й удары — обычный крио урон.

Баффы:
    A4 Prosecution Edict — сразу 5 стаков: +30% АТК;
    Radiance — +30% урона звёздного проводника (SC_BONUS);
    C1 — +50% урона SC 5-го удара после Luster и +50% урона Luster после
         5-го удара (окно WRIO_C1: 5-й удар первого круга его не получает);
    C6 — +10% КШ / +80% КУ усиленным ударам и Luster, сосульки 20% урона
         5-го удара и Luster (звёздный проводник).

Окно THEOSIS (Guidance of Theosis Николь) стоит на всех ударах после первой
связки N5 CA.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, stellar_conduct
from ..tags import *

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
NA_MV = {1: 1.0548, 2: 1.0239, 3: 1.3288, 4: 0.7493, 5: 1.7937}   # 4-й удар — 2 инстанса
CA_MV = 2.7533
CHILLING_PENALTY = 1.7031         # усиленный удар: 170.31% урона обычной атаки

SC_SHARE = {3: 0.60, 5: 0.80, "ca": 1.00}       # Radiance: доля исходного урона как SC
SC_SHARE_C2 = {3: 0.90, 5: 1.20, "ca": 1.50}    # C2 (5 стаков Prosecution Edict)

A4_ATK = 0.06 * 5                 # Prosecution Edict: +6% АТК × 5 стаков
RADIANCE_SC_BONUS = 0.30          # +30% урона звёздного проводника
C1_SC_BONUS = 0.50                # C1: +50% урона
C6_CRIT_RATE = 0.10               # C6: +10% КШ
C6_CRIT_DMG = 0.80                # C6: +80% КУ
C6_ICICLE = 0.20                  # C6: сосулька — 20% урона 5-го удара / Luster

LOOPS = 3                         # 3 × (N5 CA)

#: Стаки «полярности» для звёздного проводника Ризли (основной на поле)
WRIO_POLAR_STACKS = 7


def _na(n: int) -> float:
    """Множитель усиленного удара n (обычной атаки × Chilling Penalty)."""
    return NA_MV[n] * CHILLING_PENALTY


WRIO_KIT = Character(
    name="Ризли",
    element="cryo",
    weapon_type="catalyst",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 311.0,
        S.CRIT_VALUE: 0.984,
    },
    buffs=(
        Buff(S.ATK_PCT, A4_ATK, target=SELF,
             source="There Shall Be a Reckoning for Sin: +30% АТК (5 стаков)"),
        Buff(S.SC_BONUS, RADIANCE_SC_BONUS, target=SELF,
             source="There Shall Be an Unveiling for Injustice: +30% урона звёздного проводника"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff(S.SC_BONUS, C1_SC_BONUS, target=SELF, requires=(WRIO_C1,),
                     source="C1 Ризли: +50% урона 5-го удара / Luster: Vaulting Fist"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            patches={
                "3-й удар — SC": lambda s: replace(s, mv=_na(3) * SC_SHARE_C2[3]),
                "5-й удар — SC": lambda s: replace(s, mv=_na(5) * SC_SHARE_C2[5]),
                "Luster: Vaulting Fist — SC": lambda s: replace(s, mv=CA_MV * SC_SHARE_C2["ca"]),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("crit_value.normal", C6_CRIT_RATE * 2 + C6_CRIT_DMG, target=SELF,
                     source="C6 Ризли: +10% КШ / +80% КУ усиленным ударам"),
                Buff("crit_value.charged", C6_CRIT_RATE * 2 + C6_CRIT_DMG, target=SELF,
                     source="C6 Ризли: +10% КШ / +80% КУ Luster: Vaulting Fist"),
            ),
        ),
    },
    note="ДД звёздного проводника.",
)

#: Окна отряда, в которых находится Ризли. Расставляйте, как нужно.
_FIRST = (ON,TTDS_HALF)                     # первая связка N5 CA
_LATER = (ON, THEOSIS,TTDS_HALF)             # остальные — под Guidance of Theosis Николь


def _occ_all(per_loop: float = 1):
    """Удар в каждом из 3 кругов: 1-й без Theosis, 2-й и 3-й — с ним."""
    return [occ(per_loop, *_FIRST), occ(per_loop * (LOOPS - 1), *_LATER)]


WRIO_COMBO_DICT = {
    "sc_n5ca": with_rotation(
        WRIO_KIT,
        sources=(
            elemental("1-й удар", "atk", _na(1), "cryo", "normal", _occ_all()),
            elemental("2-й удар", "atk", _na(2), "cryo", "normal", _occ_all()),
            stellar_conduct("3-й удар — SC", "atk", _na(3) * SC_SHARE[3], "cryo",
                            _occ_all(), kind="normal", polar_stacks=WRIO_POLAR_STACKS),
            elemental("4-й удар (2 инстанса)", "atk", _na(4), "cryo", "normal", _occ_all(2)),
            # 5-й удар первого круга идёт до первой Luster — без бонуса C1
            stellar_conduct("5-й удар — SC", "atk", _na(5) * SC_SHARE[5], "cryo",
                            [occ(1, *_FIRST), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                            kind="normal", polar_stacks=WRIO_POLAR_STACKS),
            stellar_conduct("Luster: Vaulting Fist — SC", "atk", CA_MV * SC_SHARE["ca"], "cryo",
                            [occ(1, *_FIRST, WRIO_C1), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                            kind="charged", polar_stacks=WRIO_POLAR_STACKS),
        ),
        constellation_sources={
            # C6 включает C2 — сосульки считаются от множителей C2
            6: (
                stellar_conduct("C6: сосулька 5-го удара — SC", "atk",
                                _na(5) * SC_SHARE_C2[5] * C6_ICICLE, "cryo",
                                [occ(1, *_FIRST), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                                kind="icicle", polar_stacks=WRIO_POLAR_STACKS),
                stellar_conduct("C6: сосулька Luster — SC", "atk",
                                CA_MV * SC_SHARE_C2["ca"] * C6_ICICLE, "cryo",
                                [occ(1, *_FIRST, WRIO_C1), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                                kind="icicle", polar_stacks=WRIO_POLAR_STACKS),
            ),
        },
    ),
    "sc_n5ca_4": with_rotation(
        WRIO_KIT,
        sources=(
            elemental("1-й удар", "atk", _na(1), "cryo", "normal", _occ_all()),
            elemental("2-й удар", "atk", _na(2), "cryo", "normal", _occ_all()),
            stellar_conduct("3-й удар — SC", "atk", _na(3) * SC_SHARE[3], "cryo",
                            _occ_all(), kind="normal", polar_stacks=WRIO_POLAR_STACKS),
            stellar_conduct("3-й удар — SC", "atk", _na(3) * SC_SHARE[3], "cryo",
                            [occ(1, *_LATER)], kind="normal", polar_stacks=WRIO_POLAR_STACKS),
            elemental("4-й удар (2 инстанса)", "atk", _na(4), "cryo", "normal", _occ_all(2)),
            # 5-й удар первого круга идёт до первой Luster — без бонуса C1
            stellar_conduct("5-й удар — SC", "atk", _na(5) * SC_SHARE[5], "cryo",
                            [occ(1, *_FIRST), occ(LOOPS, *_LATER, WRIO_C1)],
                            kind="normal", polar_stacks=WRIO_POLAR_STACKS),
            stellar_conduct("Luster: Vaulting Fist — SC", "atk", CA_MV * SC_SHARE["ca"], "cryo",
                            [occ(1, *_FIRST, WRIO_C1), occ(LOOPS, *_LATER, WRIO_C1)],
                            kind="charged", polar_stacks=WRIO_POLAR_STACKS),
        ),
        constellation_sources={
            # C6 включает C2 — сосульки считаются от множителей C2
            6: (
                stellar_conduct("C6: сосулька 5-го удара — SC", "atk",
                                _na(5) * SC_SHARE_C2[5] * C6_ICICLE, "cryo",
                                [occ(1, *_FIRST), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                                kind="icicle", polar_stacks=WRIO_POLAR_STACKS),
                stellar_conduct("C6: сосулька Luster — SC", "atk",
                                CA_MV * SC_SHARE_C2["ca"] * C6_ICICLE, "cryo",
                                [occ(1, *_FIRST, WRIO_C1), occ(LOOPS - 1, *_LATER, WRIO_C1)],
                                kind="icicle", polar_stacks=WRIO_POLAR_STACKS),
            ),
        },
    ),
}

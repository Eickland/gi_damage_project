"""
Цзы Бай — гео, ДД отрядов лунной кристаллизации. Масштабируется от ЗАЩИТЫ.

Базовое комбо: E N4 sE N4 sE Q N4 sE N4 sE, 14.8 с
    C1: E sE N4 sE N4 sE Q N4 sE N4 sE — +1 sE в самом начале (его и усиливает
    C1), +0.3 с анимации (ZIBAI_C1_EXTRA_TIME); все 4 серии N4 идут после sE.
    E   — Heaven and Earth Made Manifest (вход в Lunar Phase Shift, без урона)
    N4  — 4 обычные атаки (гео); 4-й удар даёт доп. удар — прямая лунная
          кристаллизация (53.02% ЗЩ)
    sE  — Spirit Steed's Stride: 1-й удар гео, 2-й — прямая лунная кристаллизация
    Q   — Tri-Sphere Eminence: 1-й удар гео, 2-й — прямая лунная кристаллизация

Баффы (постоянные):
    A1  Selenic Descent: 2-й удар sE + 60% ЗЩ (доп. базовый урон); C2: ещё +550%
    A4  Layered Peaks: +15% ЗЩ за каждого ДРУГОГО гео, +60 МС за каждого гидро
        (считается по составу отряда автоматически)
    Moonsign: +0.7% базового урона лунной кристаллизации за 100 ЗЩ (макс. 14%) отряду
    C1  доп. sE в начале комбо: его 2-й удар +220% (лунный бонус урона)
    C2  +30% урона лунной кристаллизации отряду
    C4  доп. удар 4-й атаки после sE — 250% урона (C0: 3 из 4, с C1: все 4)
    C6  всегда полный: Radiance максимум (PHASE_RADIANCE_MAX) → +1.6% возвышения
        за очко сверх 70 для sE и всей лунной кристаллизации Цзы Бай

Окна отряда: NIGHTINGALE (Nightingale's Song Иллуги) — на всех ударах,
FIELD_CATALOG (C1 Линеи) — на ударах лунной кристаллизации.

Допущения: A1 (Selenic Descent) действует на все sE; максимум Phase Shift
Radiance для C6 — 100.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, lunar_crystallize
from ..tags import *

ZIBAI_NAME = "Цзы Бай"

# --------------------------------------------------------------------------- #
#  Множители (в долях ЗЩ)                                                      #
# --------------------------------------------------------------------------- #
NA_MV = {1: 1.0184, 2: 0.9378, 3: 0.6222, 4: 1.5692}          # 3-й удар — 2 инстанса
NA_MV_C3 = {1: 1.2023, 2: 1.1071, 3: 0.7346, 4: 1.8525}
NA4_EXTRA_MV, NA4_EXTRA_MV_C3 = 0.5302, 0.6259                 # доп. удар 4-й атаки (LC)
STRIDE_MV = {1: 3.1055, 2: 2.5374}                             # Spirit Steed's Stride
STRIDE_MV_C3 = {1: 3.6662, 2: 2.9956}
BURST_MV = {1: 2.2853, 2: 3.1994}                              # Tri-Sphere Eminence
BURST_MV_C5 = {1: 2.6979, 2: 3.7771}

A1_DEF = 0.60                  # Selenic Descent: +60% ЗЩ ко 2-му удару sE
C2_A1_DEF = 5.50               # C2: ещё +550% ЗЩ
A4_DEF_PER_GEO = 0.15          # +15% ЗЩ за другого гео
A4_EM_PER_HYDRO = 60.0         # +60 МС за гидро
MOONSIGN_PER_100_DEF = 0.007   # +0.7% базового урона LC за 100 ЗЩ
MOONSIGN_CAP = 0.14
C1_BONUS = 2.20                # C1: +220%
C2_LC_BONUS = 0.30             # C2: +30% урона лунной кристаллизации отряду
C4_EXTRA_MULT = 2.50           # C4: доп. удар 4-й атаки — 250% исходного урона
PHASE_RADIANCE_MAX = 100       # C6: тратится вся Radiance (считаем полной)
C6_ELEVATION = 0.016 * (PHASE_RADIANCE_MAX - 70)   # 0.48

#: Теги источников
STRIDE_1 = "zibai_stride"      # 1-й удар sE (гео)
STRIDE_2 = "zibai_stride2"     # 2-й удар sE (лунная кристаллизация)

LOOPS_NA = 4                   # N4 × 4
LOOPS_STRIDE = 4               # sE × 4 (C1: 5)
ZIBAI_TIME = 14.1              # длительность комбо, с
ZIBAI_C1_EXTRA_TIME = 0.3      # C1: анимация доп. sE


def _zibai_def(ctx) -> float:
    return ctx.stat(ZIBAI_NAME, "def", frozenset({ON}))


ZIBAI_KIT = Character(
    name=ZIBAI_NAME,
    element="geo",
    weapon_type="sword",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_DEF: 957.0,
        S.CRIT_VALUE: 0.988,
    },
    buffs=(
        Buff(f"{S.FLAT_BASE_DMG}.{STRIDE_2}", lambda ctx: A1_DEF * ctx.own("def"),
             target=SELF, source="Selenic Descent: 2-й удар sE +60% ЗЩ"),
        Buff(S.DEF_PCT, lambda ctx: A4_DEF_PER_GEO * ctx.count_element("geo"),
             target=SELF, source="Layered Peaks: +15% ЗЩ за каждого другого гео"),
        Buff(S.BASE_EM, lambda ctx: A4_EM_PER_HYDRO * ctx.count_element("hydro"),
             target=SELF, source="Layered Peaks: +60 МС за каждого гидро"),
        Buff(f"{S.LUNAR_BASE_INC}.lunar_crystallize",
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_100_DEF * _zibai_def(ctx) / 100.0),
             target=TEAM,
             source="Moonsign Benediction: +0.7% базового урона LC за 100 ЗЩ (макс. 14%)"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(
                Buff(S.LUNAR_BONUS, C1_BONUS, target=SELF, requires=(ZIBAI_C1,),
                     source="C1: первый sE после входа в режим, 2-й удар +220%"),
            ),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(f"{S.LUNAR_BONUS}.lunar_crystallize", C2_LC_BONUS, target=TEAM,
                     source="C2: +30% урона лунной кристаллизации отряду"),
                Buff(f"{S.FLAT_BASE_DMG}.{STRIDE_2}", lambda ctx: C2_A1_DEF * ctx.own("def"),
                     target=SELF, source="C2: 2-й удар sE ещё +550% ЗЩ"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            patches={
                "1-й удар": lambda s: replace(s, mv=NA_MV_C3[1]),
                "2-й удар": lambda s: replace(s, mv=NA_MV_C3[2]),
                "3-й удар (2 инстанса)": lambda s: replace(s, mv=NA_MV_C3[3]),
                "4-й удар": lambda s: replace(s, mv=NA_MV_C3[4]),
                "4-й удар — доп. (LC)": lambda s: replace(s, mv=NA4_EXTRA_MV_C3),
                "4-й удар — доп. после sE (LC)": lambda s: replace(s, mv=NA4_EXTRA_MV_C3),
                "Spirit Steed's Stride — 1-й удар": lambda s: replace(s, mv=STRIDE_MV_C3[1]),
                "Spirit Steed's Stride — 2-й удар (LC)": lambda s: replace(s, mv=STRIDE_MV_C3[2]),
            },
        ),
        4: Constellation(
            number=4, name="C4",
            # применяется после C3 — умножаем текущий множитель
            patches={
                "4-й удар — доп. после sE (LC)": lambda s: replace(s, mv=s.mv * C4_EXTRA_MULT), # type: ignore
            },
        ),
        5: Constellation(
            number=5, name="C5",
            patches={
                "Tri-Sphere Eminence — 1-й удар": lambda s: replace(s, mv=BURST_MV_C5[1]),
                "Tri-Sphere Eminence — 2-й удар (LC)": lambda s: replace(s, mv=BURST_MV_C5[2]),
            },
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(
                Buff(f"elevation.{STRIDE_1}", C6_ELEVATION, target=SELF,
                     source="C6: возвышение 1-го удара sE +48%"),
                Buff("elevation.lunar_crystallize", C6_ELEVATION, target=SELF,
                     source="C6: возвышение лунной кристаллизации Цзы Бай +48%"),
            ),
        ),
    },
    note="ДД лунной кристаллизации, масштабирование от ЗЩ.",
)

#: Окна отряда: все удары под Nightingale's Song Иллуги,
#: удары лунной кристаллизации ещё и тратят Field Catalog Линеи.
_TAGS = (ON, NIGHTINGALE)
_LC_TAGS = (ON, NIGHTINGALE, FIELD_CATALOG)

ZIBAI_COMBO_DICT = {
    # E N4 sE N4 sE Q N4 sE N4 sE — 14.8 с (C1: +sE в начале, +0.3 с)
    "lc_combo": with_rotation(
        ZIBAI_KIT,
        sources=(
            elemental("1-й удар", "def", NA_MV[1], "geo", "normal", [occ(LOOPS_NA, *_TAGS)]),
            elemental("2-й удар", "def", NA_MV[2], "geo", "normal", [occ(LOOPS_NA, *_TAGS)]),
            elemental("3-й удар (2 инстанса)", "def", NA_MV[3], "geo", "normal",
                      [occ(LOOPS_NA * 2, *_TAGS)]),
            elemental("4-й удар", "def", NA_MV[4], "geo", "normal", [occ(LOOPS_NA, *_TAGS)]),
            # C0: первая N4 идёт сразу после E — без C4; остальные три — после sE
            lunar_crystallize("4-й удар — доп. (LC)", "def", NA4_EXTRA_MV,
                              [occ(1, *_LC_TAGS,INST)], kind="normal"),
            lunar_crystallize("4-й удар — доп. после sE (LC)", "def", NA4_EXTRA_MV,
                              [occ(LOOPS_NA - 1, *_LC_TAGS)], kind="normal"),
            elemental("Spirit Steed's Stride — 1-й удар", "def", STRIDE_MV[1], "geo", "skill",
                      [occ(LOOPS_STRIDE, *_TAGS)], extra_tags=(STRIDE_1,)),
            lunar_crystallize("Spirit Steed's Stride — 2-й удар (LC)", "def", STRIDE_MV[2],
                              [occ(LOOPS_STRIDE-2, *_LC_TAGS)],
                              kind="skill", extra_tags=(STRIDE_2,)),
            lunar_crystallize("Spirit Steed's Stride — 2-й удар (LC)", "def", STRIDE_MV[2],
                              [occ(2, *_LC_TAGS,INST)],
                              kind="skill", extra_tags=(STRIDE_2,)),
            elemental("Tri-Sphere Eminence — 1-й удар", "def", BURST_MV[1], "geo", "burst",
                      [occ(1, *_TAGS)]),
            lunar_crystallize("Tri-Sphere Eminence — 2-й удар (LC)", "def", BURST_MV[2],
                              [occ(1, *_LC_TAGS,INST)], kind="burst"),
        ),
        constellation_patches={
            1: {
                # +1 sE в начале: он и получает +220% (окно ZIBAI_C1)
                "Spirit Steed's Stride — 1-й удар": lambda s: replace(
                    s, occurrences=[occ(LOOPS_STRIDE + 1, *_TAGS)]),
                "Spirit Steed's Stride — 2-й удар (LC)": lambda s: replace(
                    s, occurrences=[occ(1, *_LC_TAGS, ZIBAI_C1),
                                    occ(LOOPS_STRIDE, *_LC_TAGS)]),
                # теперь все 4 серии N4 идут после sE
                "4-й удар — доп. (LC)": lambda s: replace(s, occurrences=[]),
                "4-й удар — доп. после sE (LC)": lambda s: replace(
                    s, occurrences=[occ(LOOPS_NA, *_LC_TAGS)]),
            },
        },
    ),
}


def zibai_time(constellation: int) -> float:
    """Длительность комбо с учётом доп. sE на C1+."""
    return ZIBAI_TIME + (ZIBAI_C1_EXTRA_TIME if constellation >= 1 else 0.0)

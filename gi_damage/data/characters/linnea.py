"""
Линея — гео, лук. Саппорт лунной кристаллизации (Moonsign). Масштабируется
от ЗАЩИТЫ. Навык работает из кармана. Ротация: E, 1.2 с.

Комбо — только обычная форма (Super Power Form) Люми:
    16 × Pound-Pound Pummeler   (гео, 172.8% ЗЩ)
     4 × Heavy Overdrive Hammer (прямая лунная кристаллизация, 180% ЗЩ)

Баффы (постоянные; Ascendant Gleam считается активным — все в отряде Moonsign):
    A1  Field Observation Notes: −15% гео сопротивления, Ascendant Gleam ещё −15%
    A4  Universal Naturalist Archive: активному Moonsign-персонажу +МС = 5% ЗЩ Линеи
    Moonsign: +0.7% базового урона лунной кристаллизации за 100 ЗЩ (макс. 14%)
    C1  Field Catalog: удар лунной кристаллизации (окно FIELD_CATALOG) получает
        доп. базовый урон = 75% ЗЩ Линеи (18 стаков)
    C2  +40% КУ гео и гидро персонажам отряда; Ascendant Gleam: каждый
        Heavy Overdrive Hammer вызывает Moondrift Harmony, в которой все гидро
        и гео персонажи — участники: доля каждого 0.6 (LINNEA_C2_WEIGHTS;
        реакции — в отряде)
    C3  новые множители
    C4  +25% ЗЩ Линее и активному персонажу
    C6  Field Catalog: ×1.5 (112.5% ЗЩ), +25% возвышения лунной кристаллизации отряду

Million Ton Crush (Ultimate Power Form) пока не используется — константы есть.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, lunar_crystallize
from ..tags import *

LINNEA_NAME = "Линея"

# --------------------------------------------------------------------------- #
#  Множители (в долях ЗЩ)                                                      #
# --------------------------------------------------------------------------- #
PUMMELER_MV, PUMMELER_MV_C3 = 1.728, 2.04
HAMMER_MV, HAMMER_MV_C3 = 1.80, 2.125
CRUSH_MV, CRUSH_MV_C3 = 7.20, 8.50        # Million Ton Crush (пока не в комбо)

PUMMELER_HITS = 16
HAMMER_HITS = 4

A1_GEO_RES = 0.15 + 0.15       # −15% и ещё −15% (Ascendant Gleam)
A4_EM_PER_DEF = 0.05           # +МС активному = 5% ЗЩ Линеи
MOONSIGN_PER_100_DEF = 0.007
MOONSIGN_CAP = 0.14
C1_CATALOG_DEF = 0.75          # Field Catalog: +75% ЗЩ за стак
C6_CATALOG_MULT = 1.5          # C6: ×1.5
C2_CRIT_DMG = 0.40
C4_DEF = 0.25
C6_LC_ELEVATION = 0.25

LINNEA_TIME = 1.2

#: C2 (Ascendant Gleam): в Moondrift Harmony от Heavy Overdrive Hammer все гидро
#: и гео персонажи считаются участниками — каждый вносит долю 0.6 (а не 60/30/5/5)
LINNEA_C2_WEIGHTS = (0.6, 0.3, 0.05, 0.05)


def _linnea_def(ctx) -> float:
    return ctx.stat(LINNEA_NAME, "def", frozenset({OFF}))


LINNEA_KIT = Character(
    name=LINNEA_NAME,
    element="geo",
    weapon_type="bow",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_DEF: 907.0,
        S.CRIT_VALUE: 0.988,
    },
    buffs=(
        Buff("res_reduction.geo", A1_GEO_RES, target=TEAM,
             source="Field Observation Notes: −30% гео сопротивления (с Ascendant Gleam)"),
        Buff(S.FLAT_EM, lambda ctx: A4_EM_PER_DEF * _linnea_def(ctx),
             target=OTHERS, requires=(ON,),
             source="Universal Naturalist Archive: активному Moonsign +МС = 5% ЗЩ Линеи"),
        Buff(f"{S.LUNAR_BASE_INC}.lunar_crystallize",
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_100_DEF * _linnea_def(ctx) / 100.0),
             target=TEAM,
             source="Habitat Survey: +0.7% базового урона LC за 100 ЗЩ (макс. 14%)"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(
                Buff(f"{S.FLAT_BASE_DMG}.lunar_crystallize",
                     lambda ctx: C1_CATALOG_DEF * _linnea_def(ctx),
                     target=TEAM, requires=(FIELD_CATALOG,),
                     source="C1 Линеи: Field Catalog, +75% ЗЩ Линеи к удару LC"),
            ),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(S.CRIT_VALUE,
                     lambda ctx: C2_CRIT_DMG if ctx.recipient_element() in ("geo", "hydro") else 0.0,
                     target=TEAM,
                     source="C2 Линеи: +40% КУ гео и гидро персонажам"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            patches={
                "Люми: Pound-Pound Pummeler": lambda s: replace(s, mv=PUMMELER_MV_C3),
                "Люми: Heavy Overdrive Hammer (LC)": lambda s: replace(s, mv=HAMMER_MV_C3),
            },
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff(S.DEF_PCT, C4_DEF, target=SELF, source="C4 Линеи: +25% ЗЩ"),
                Buff(S.DEF_PCT, C4_DEF, target=OTHERS, requires=(ON,),
                     source="C4 Линеи: +25% ЗЩ активному персонажу"),
            ),
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(
                # Field Catalog ×1.5: добавляем недостающие +50% от исходного
                Buff(f"{S.FLAT_BASE_DMG}.lunar_crystallize",
                     lambda ctx: C1_CATALOG_DEF * (C6_CATALOG_MULT - 1.0) * _linnea_def(ctx),
                     target=TEAM, requires=(FIELD_CATALOG,),
                     source="C6 Линеи: Field Catalog ×1.5"),
                Buff("elevation.lunar_crystallize", C6_LC_ELEVATION, target=TEAM,
                     source="C6 Линеи: +25% возвышения лунной кристаллизации"),
            ),
        ),
    },
    note="Саппорт лунной кристаллизации (Moonsign).",
)

LINNEA_COMBO_DICT = {
    "super_power": with_rotation(
        LINNEA_KIT,
        sources=(
            elemental("Люми: Pound-Pound Pummeler", "def", PUMMELER_MV, "geo", "skill",
                      [occ(PUMMELER_HITS, OFF)]),
            lunar_crystallize("Люми: Heavy Overdrive Hammer (LC)", "def", HAMMER_MV,
                              [occ(HAMMER_HITS, OFF, FIELD_CATALOG)], kind="skill"),
        ),
    ),
}

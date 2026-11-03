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
    C2  +40% КУ гео и гидро персонажам отряда; +150% КУ удару Million Ton Crush;
        Ascendant Gleam: удары Люми вызывают Moondrift Harmony (обычные
        реакции, считаются в отряде — число зависит от комбо, см. файл отряда)
    C3  новые множители
    C4  +25% ЗЩ Линее и активному персонажу
    C6  Field Catalog: ×1.5 (112.5% ЗЩ), +25% возвышения лунной кристаллизации отряду

Комбо ultra_power (Ultimate Power Form): 8 × Pummeler + 1 × Million Ton Crush
(прямая лунная кристаллизация, 720% ЗЩ, C3 — 850%).
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
CRUSH_MV, CRUSH_MV_C3 = 7.20, 8.50        # Million Ton Crush (ultra_power)

PUMMELER_HITS = 16
PUMMELER_HITS_ULTRA = 8
HAMMER_HITS = 4

A1_GEO_RES = 0.15 + 0.15       # −15% и ещё −15% (Ascendant Gleam)
A4_EM_PER_DEF = 0.05           # +МС активному = 5% ЗЩ Линеи
MOONSIGN_PER_100_DEF = 0.007
MOONSIGN_CAP = 0.14
C1_CATALOG_DEF = 0.75          # Field Catalog: +75% ЗЩ за стак
C6_CATALOG_MULT = 1.5          # C6: ×1.5
C2_CRIT_DMG = 0.40
C2_CRUSH_CRIT_DMG = 1.50       # C2: +150% КУ удару Million Ton Crush
C4_DEF = 0.25
C6_LC_ELEVATION = 0.25

LINNEA_TIME = 1.2

#: Тег удара Million Ton Crush — на него вешается крит. урон от C2
CRUSH_TAG = "linnea_crush"
CRUSH_NAME = "Люми: Million Ton Crush (LC)"



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
                # Оба ключа: crit_value — для режимов по крит-вэлью (balance),
                # crit_dmg — для expected/always. Лишний ключ в другом режиме не читается.
                Buff(f"{S.CRIT_VALUE}.{CRUSH_TAG}", C2_CRUSH_CRIT_DMG, target=SELF,
                     source="C2 Линеи: +150% КУ удару Million Ton Crush"),
                Buff(f"{S.CRIT_DMG}.{CRUSH_TAG}", C2_CRUSH_CRIT_DMG, target=SELF,
                     source="C2 Линеи: +150% КУ удару Million Ton Crush"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            patches={
                "Люми: Pound-Pound Pummeler": lambda s: replace(s, mv=PUMMELER_MV_C3),
                "Люми: Heavy Overdrive Hammer (LC)": lambda s: replace(s, mv=HAMMER_MV_C3),
                CRUSH_NAME: lambda s: replace(s, mv=CRUSH_MV_C3),
            },
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff(S.DEF_PCT, C4_DEF, target=SELF, source="C4 Линеи: +25% ЗЩ"),
                Buff(S.DEF_PCT, C4_DEF, target=TEAM, requires=(ON,),
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
            lunar_crystallize("Луми: Heavy Overdrive Hammer (LC)", "def", HAMMER_MV,
                              [occ(HAMMER_HITS, OFF, FIELD_CATALOG)], kind="skill"),
        ),
    ),
    "ultra_power": with_rotation(
        LINNEA_KIT,
        sources=(
            elemental("Луми: Pound-Pound Pummeler", "def", PUMMELER_MV, "geo", "skill",
                      [occ(PUMMELER_HITS_ULTRA, OFF)]),
            # Своё имя: иначе патч C3 для Hammer подменит mv на 212.5%
            lunar_crystallize(CRUSH_NAME, "def", CRUSH_MV,
                              [occ(1, ON, FIELD_CATALOG,AUBADE_SPECIAL)], kind="skill",
                              extra_tags=(CRUSH_TAG,)),
        ),
    ),
}


def linnea_combo_name(character: Character) -> str:
    """Ключ LINNEA_COMBO_DICT, из которого сделан персонаж.

    Сначала по самому объекту, иначе — по набору ударов (на случай копий):
    есть Million Ton Crush → "ultra_power", иначе "super_power".
    """
    for key, combo in LINNEA_COMBO_DICT.items():
        if character is combo:
            return key
    names = {s.name for s in character.sources}
    return "ultra_power" if CRUSH_NAME in names else "super_power"

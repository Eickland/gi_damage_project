"""
Колумбина — гидро, катализатор. Саппорт лунных реакций (Moonsign).
Масштабируется от HP. Навык работает из кармана. Ротация: E Q, 3.1 с.

Комбо (за ротацию отряда):
    E                      — 1 удар навыка (гидро)
    Gravity Ripple         — 10 ударов (гидро, вне поля)
    Gravity Interference   — 3 удара лунной кристаллизации (вне поля, раз в 6 с)
        C1: +1 удар сразу при E (с поля);  C2: ещё +2 удара (вне поля)
    Q                      — 1 удар взрыва (гидро)

Баффы (постоянные):
    Q   Lunar Domain: +40% урона лунных реакций отряду (C5: 49%)
    A1  Lunacy: +15% КШ (3 стака)
    A4  Law of the New Moon: каждый Moondrift с шансом 33% наносит доп. атаку —
        в среднем ×1.33 к числу ударов лунных клеток (MOONDRIFT_EXTRA, считается
        в отряде)
    Moonsign Benediction: +0.2% базового урона лунных реакций за 1000 HP (макс. 7%)
    C1, C3, C4, C5: +1.5% возвышения лунных реакций отряду каждое
    C2, C6: +7% возвышения лунных реакций отряду каждое
    C2  Lunar Brilliance: +40% HP; активному персонажу +ЗЩ = 1% HP Колумбины
    C4  Gravity Interference от C1: +12.5% HP (доп. базовый урон)
    C6  +80% КУ гео и гидро урона отряду (лунная кристаллизация = гео + гидро)

Gravity Interference — урон лунной кристаллизации; стихия — гео (как у всей
лунной кристаллизации).
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, lunar_crystallize
from ..tags import *

COLUMBINA_NAME = "Колумбина"

# --------------------------------------------------------------------------- #
#  Множители (в долях Max HP)                                                  #
# --------------------------------------------------------------------------- #
SKILL_MV, SKILL_MV_C3 = 0.301, 0.3553
RIPPLE_MV, RIPPLE_MV_C3 = 0.1685, 0.1989
INTERFERENCE_MV, INTERFERENCE_MV_C3 = 0.1588, 0.1875
BURST_MV, BURST_MV_C5 = 0.5803, 0.6851
DOMAIN_LUNAR_BONUS, DOMAIN_LUNAR_BONUS_C5 = 0.40, 0.49

RIPPLE_HITS = 10
INTERFERENCE_HITS = 3          # C0, раз в 6 с
C2_EXTRA_INTERFERENCE = 1

A1_CRIT_RATE = 0.05 * 3        # Lunacy: +5% КШ × 3
MOONDRIFT_EXTRA = 0.33         # A4: шанс доп. атаки каждого Moondrift
MOONSIGN_PER_1000_HP = 0.002   # +0.2% базового урона за 1000 HP
MOONSIGN_CAP = 0.07
SMALL_ELEVATION = 0.015        # C1/C3/C4/C5
BIG_ELEVATION = 0.07           # C2/C6
C2_HP = 0.40
C2_DEF_PER_HP = 0.01
C4_FLAT_HP = 0.125
C6_CRIT_DMG = 0.80

COLUMBINA_TIME = 3.1

#: Тег источника: Gravity Interference от C1 (C4 добавляет ему доп. урон)
INTERFERENCE_C1 = "columbina_gi_c1"


def _columbina_hp(ctx) -> float:
    return ctx.stat(COLUMBINA_NAME, "hp", frozenset({OFF}))


COLUMBINA_KIT = Character(
    name=COLUMBINA_NAME,
    element="hydro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_HP: 14695.0,
        S.CRIT_VALUE: 0.988,
    },
    buffs=(
        Buff(S.LUNAR_BONUS, DOMAIN_LUNAR_BONUS, target=TEAM,
             source="Lunar Domain: +40% урона лунных реакций отряду"),
        Buff(S.CRIT_VALUE, A1_CRIT_RATE * 2, target=SELF,
             source="Lunacy's Lure: +15% КШ (3 стака)"),
        Buff(S.LUNAR_BASE_INC,
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_1000_HP * _columbina_hp(ctx) / 1000.0),
             target=TEAM,
             source="Moonsign Benediction: +0.2% базового урона лунных реакций за 1000 HP (макс. 7%)"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                        source="C1 Колумбины: +1.5% возвышения лунных реакций"),),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(S.HP_PCT, C2_HP, target=SELF,
                     source="C2 Колумбины: Lunar Brilliance, +40% HP"),
                Buff(S.FLAT_DEF, lambda ctx: C2_DEF_PER_HP * _columbina_hp(ctx),
                     target=TEAM, requires=(ON,),
                     source="C2 Колумбины: активному +ЗЩ = 1% HP Колумбины"),
                Buff("elevation.lunar", BIG_ELEVATION, target=TEAM,
                     source="C2 Колумбины: +7% возвышения лунных реакций"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            buffs=(Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                        source="C3 Колумбины: +1.5% возвышения лунных реакций"),),
            patches={
                "Навык": lambda s: replace(s, mv=SKILL_MV_C3),
                "Gravity Ripple": lambda s: replace(s, mv=RIPPLE_MV_C3),
                "Gravity Interference (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
                "C1: Gravity Interference при E (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
                "C2: доп. Gravity Interference (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
            },
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff(f"{S.FLAT_BASE_DMG}.{INTERFERENCE_C1}",
                     lambda ctx: C4_FLAT_HP * ctx.own("hp"), target=SELF,
                     source="C4 Колумбины: Gravity Interference от C1 +12.5% HP"),
                Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                     source="C4 Колумбины: +1.5% возвышения лунных реакций"),
            ),
        ),
        5: Constellation(
            number=5, name="C5",
            buffs=(
                Buff(S.LUNAR_BONUS, DOMAIN_LUNAR_BONUS_C5 - DOMAIN_LUNAR_BONUS, target=TEAM,
                     source="C5 Колумбины: Lunar Domain до 49%"),
                Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                     source="C5 Колумбины: +1.5% возвышения лунных реакций"),
            ),
            patches={"Взрыв стихии": lambda s: replace(s, mv=BURST_MV_C5)},
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(
                Buff("crit_value.geo", C6_CRIT_DMG, target=TEAM,
                     source="C6 Колумбины: +80% КУ гео урона"),
                Buff("crit_value.hydro", C6_CRIT_DMG, target=TEAM,
                     source="C6 Колумбины: +80% КУ гидро урона"),
                Buff("elevation.lunar", BIG_ELEVATION, target=TEAM,
                     source="C6 Колумбины: +7% возвышения лунных реакций"),
            ),
        ),
    },
    note="Саппорт лунных реакций (Moonsign).",
)

#: Окна отряда. 3 обычных Gravity Interference тратят Field Catalog Линеи (C1),
#: удар от C1 (с поля) — Nightingale's Song Иллуги.
COLUMBINA_COMBO_DICT = {
    "lc_support": with_rotation(
        COLUMBINA_KIT,
        sources=(
            elemental("Навык", "hp", SKILL_MV, "hydro", "skill", [occ(1, ON)]),
            elemental("Gravity Ripple", "hp", RIPPLE_MV, "hydro", "skill",
                      [occ(RIPPLE_HITS, OFF)]),
            lunar_crystallize("Gravity Interference (LC)", "hp", INTERFERENCE_MV,
                              [occ(INTERFERENCE_HITS, OFF, FIELD_CATALOG)], kind="skill"),
            elemental("Взрыв стихии", "hp", BURST_MV, "hydro", "burst", [occ(1, ON)]),
        ),
        constellation_sources={
            1: (lunar_crystallize("C1: Gravity Interference при E (LC)", "hp", INTERFERENCE_MV,
                                  [occ(1, ON, NIGHTINGALE)], kind="skill",
                                  extra_tags=(INTERFERENCE_C1,)),),
            2: (lunar_crystallize("C2: доп. Gravity Interference (LC)", "hp", INTERFERENCE_MV,
                                  [occ(C2_EXTRA_INTERFERENCE, OFF)], kind="skill"),),
        },
    ),
}

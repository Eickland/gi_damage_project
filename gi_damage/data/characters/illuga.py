"""
Иллуги — гео, копьё. Саппорт лунной кристаллизации (Moonsign).
Масштабируется от МС и ЗЩ. Ротация: E Q, 2.4 с. C6 — базовая линия.

Nightingale's Song (взрыв, 36 стаков): удар АКТИВНОГО персонажа, помеченный
окном NIGHTINGALE, получает плоскую прибавку от МС Иллуги:
    гео урон (элементальный)           — 60.48% МС + A4 (24% МС)  → "flat_dmg.geo"
    урон лунной кристаллизации         — 406.66% МС + A4 (160% МС) → доп. базовый урон
A4 Demonhunter's Dusk: 1/2/3 гидро или гео персонажа в отряде → 7/14/24% МС
(лунная кристаллизация: 48/96/160% МС). Считается по составу отряда.

A1 Lightkeeper's Oath (остальным членам отряда): гео урону +5% КШ / +10% КУ,
Ascendant Gleam +50 МС. C6 заменяет: +10% КШ / +30% КУ, +80 МС.
C2: 5 призывов Aedon из кармана (400% МС + 200% ЗЩ, взрыв).
C4: активному персонажу +200 ЗЩ.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ
from ..tags import *

ILLUGA_NAME = "Иллуги"

# --------------------------------------------------------------------------- #
#  Множители                                                                   #
# --------------------------------------------------------------------------- #
SKILL_EM, SKILL_DEF = 10.8576, 5.4288                 # навык (удержание)
BURST_EM, BURST_DEF = 14.8896, 7.4448
BURST_EM_C3, BURST_DEF_C3 = 17.578, 8.789
SONG_GEO, SONG_GEO_C3 = 0.6048, 0.714                 # Nightingale's Song: гео урон, доли МС
SONG_LC, SONG_LC_C3 = 4.0666, 4.8008                  # … урон лунной кристаллизации
A4_GEO = {0: 0.0, 1: 0.07, 2: 0.14, 3: 0.24}          # по числу гидро/гео в отряде
A4_LC = {0: 0.0, 1: 0.48, 2: 0.96, 3: 1.60}
AEDON_EM, AEDON_DEF = 4.0, 2.0                        # C2
AEDON_HITS = 5

A1_CR, A1_CD, A1_EM = 0.05, 0.10, 50.0
C6_CR, C6_CD, C6_EM = 0.10, 0.30, 80.0
C4_DEF = 200.0

ILLUGA_TIME = 2.4


def _illuga_em(ctx) -> float:
    return ctx.stat(ILLUGA_NAME, "em", frozenset({OFF}))


def _hydro_geo_tier(ctx) -> int:
    n = ctx.count_element("geo", others_only=False) + ctx.count_element("hydro", others_only=False)
    return min(n, 3)


ILLUGA_KIT = Character(
    name=ILLUGA_NAME,
    element="geo",
    weapon_type="polearm",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_DEF: 814.0,
        S.BASE_EM: 96.0,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        Buff("flat_dmg.geo",
             lambda ctx: (SONG_GEO + A4_GEO[_hydro_geo_tier(ctx)]) * _illuga_em(ctx),
             target=TEAM, requires=(ON, NIGHTINGALE),
             source="Nightingale's Song: гео урону +60.48% МС Иллуги (+A4)"),
        Buff(f"{S.FLAT_BASE_DMG}.lunar_crystallize",
             lambda ctx: (SONG_LC + A4_LC[_hydro_geo_tier(ctx)]) * _illuga_em(ctx),
             target=TEAM, requires=(ON, NIGHTINGALE),
             source="Nightingale's Song: лунной кристаллизации +406.66% МС Иллуги (+A4)"),
        Buff("crit_value.geo", A1_CR * 2 + A1_CD, target=OTHERS,
             source="Lightkeeper's Oath: гео урону +5% КШ / +10% КУ"),
        Buff(S.BASE_EM, A1_EM, target=OTHERS,
             source="Lightkeeper's Oath (Ascendant Gleam): +50 МС"),
    ),
    sources=(),
    constellations={
        2: Constellation(number=2, name="C2"),
        3: Constellation(
            number=3, name="C3",
            buffs=(
                Buff("flat_dmg.geo", lambda ctx: (SONG_GEO_C3 - SONG_GEO) * _illuga_em(ctx),
                     target=TEAM, requires=(ON, NIGHTINGALE),
                     source="C3 Иллуги: Nightingale's Song, гео урону до 71.4% МС"),
                Buff(f"{S.FLAT_BASE_DMG}.lunar_crystallize",
                     lambda ctx: (SONG_LC_C3 - SONG_LC) * _illuga_em(ctx),
                     target=TEAM, requires=(ON, NIGHTINGALE),
                     source="C3 Иллуги: Nightingale's Song, лунной кристаллизации до 480.08% МС"),
            ),
            patches={"Взрыв стихии": lambda s: replace(
                s, mv=BURST_EM_C3, extra_scaling=(("def", BURST_DEF_C3),))},
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(Buff(S.FLAT_DEF, C4_DEF, target=TEAM, requires=(ON,),
                        source="C4 Иллуги: активному +200 ЗЩ"),),
        ),
        6: Constellation(
            number=6, name="C6",
            # C6 заменяет A1: добавляем разницу
            buffs=(
                Buff("crit_value.geo", (C6_CR - A1_CR) * 2 + (C6_CD - A1_CD), target=OTHERS,
                     source="C6 Иллуги: Lightkeeper's Oath до +10% КШ / +30% КУ"),
                Buff(S.BASE_EM, C6_EM - A1_EM, target=OTHERS,
                     source="C6 Иллуги: Lightkeeper's Oath до +80 МС"),
            ),
        ),
    },
    note="Саппорт лунной кристаллизации (Moonsign).",
)

ILLUGA_COMBO_DICT = {
    "eq": with_rotation(
        ILLUGA_KIT,
        sources=(
            elemental("Навык (удержание)", "em", SKILL_EM, "geo", "skill", [occ(1, ON)],
                      extra_scaling=(("def", SKILL_DEF),)),
            elemental("Взрыв стихии", "em", BURST_EM, "geo", "burst", [occ(1, ON)],
                      extra_scaling=(("def", BURST_DEF),)),
        ),
        constellation_sources={
            2: (elemental("C2: Aedon", "em", AEDON_EM, "geo", "burst",
                          [occ(AEDON_HITS, OFF)], extra_scaling=(("def", AEDON_DEF),)),),
        },
    ),
}

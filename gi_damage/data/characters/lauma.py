"""
Лаума — дендро, катализатор. Саппорт лунных бутонов (Moonsign).
Ротация: hE Q, 3 с. Навык работает из кармана.

    hE  — заряженный навык, всегда с 3 Verdant Dew: обычный дендро удар +
          удар лунных бутонов; 3 стака Moon Song
    Q   — 18 стаков Pale Hymn + 6 × 3 Moon Song = ещё 18 (всего 36)
    Frostgrove Sanctuary — 9 ударов из кармана (урон навыка)

Pale Hymn (окно PALE_HYMN): удар лунных бутонов получает доп. базовый урон
    400.03% МС Лаумы (C2: ещё +400%, C3: 472.26%).

Баффы (постоянные; Ascendant Gleam активен):
    A1  Light for the Frosty Night: лунным бутонам отряда +10% КШ / +20% КУ
    A4  Cleansing for the Spring: урон её навыка +0.04% за 1 МС (макс. 32%)
    Moonsign Benediction: +0.0175% базового урона лунных бутонов за 1 МС (макс. 14%)
    C2  Pale Hymn ещё +400% МС; +40% урона лунных бутонов отряду
    C3  Pale Hymn 472.26% МС
    C6  Frostgrove: ещё 8 ударов лунных бутонов 185% МС (Pale Hymn не тратят);
        +25% возвышения лунных бутонов отряду

ВНИМАНИЕ: в описании нет множителей урона навыка (удержание: обычный удар
и удар лунных бутонов), Frostgrove Sanctuary и величины снижения дендро/гидро
сопротивления от навыка — константы ниже стоят 0.0, впишите значения.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, lunar_bloom
from ..tags import *

LAUMA_NAME = "Лаума"

# --------------------------------------------------------------------------- #
#  Множители (TODO: не даны в описании)                                         #
# --------------------------------------------------------------------------- #
HOLD_SKILL_EM = 2.8454            # TODO: удержание — обычный дендро удар, доли МС
HOLD_SKILL_LB_EM = 273.6*3         # TODO: удержание — удар лунных бутонов, доли МС
SANCTUARY_EM = 345.6             # TODO: удар Frostgrove Sanctuary, доли МС
SKILL_RES_SHRED = 0.25          # TODO: снижение дендро и гидро сопротивления от навыка
SANCTUARY_HITS = 9

PALE_HYMN_LB, PALE_HYMN_LB_C3 = 4.0003, 4.7226   # доп. урон лунных бутонов, доли МС
C2_PALE_HYMN_LB = 4.00
A1_CR, A1_CD = 0.10, 0.20
A4_PER_EM, A4_CAP = 0.0004, 0.32
MOONSIGN_PER_EM, MOONSIGN_CAP = 0.000175, 0.14
C2_LB_BONUS = 0.40
C6_SANCTUARY_LB_EM = 1.85
C6_SANCTUARY_LB_HITS = 8
C6_ELEVATION = 0.25

LAUMA_TIME = 3.0


def _lauma_em(ctx) -> float:
    return ctx.stat(LAUMA_NAME, "em", frozenset({OFF}))


LAUMA_KIT = Character(
    name=LAUMA_NAME,
    element="dendro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 255.0,
        S.BASE_EM: 315.0,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        Buff(f"{S.FLAT_BASE_DMG}.lunar_bloom",
             lambda ctx: PALE_HYMN_LB * _lauma_em(ctx),
             target=TEAM, requires=(PALE_HYMN,),
             source="Pale Hymn: лунным бутонам +400.03% МС Лаумы"),
        Buff("res_reduction.dendro", SKILL_RES_SHRED, target=TEAM,
             source="Навык Лаумы: снижение дендро сопротивления (TODO)"),
        Buff("res_reduction.hydro", SKILL_RES_SHRED, target=TEAM,
             source="Навык Лаумы: снижение гидро сопротивления (TODO)"),
        Buff("crit_value.lunar_bloom", A1_CR * 2 + A1_CD, target=TEAM,
             source="Light for the Frosty Night: лунным бутонам +10% КШ / +20% КУ"),
        Buff("dmg_bonus.skill", lambda ctx: min(A4_CAP, A4_PER_EM * ctx.own("em")),
             target=SELF, source="Cleansing for the Spring: урон навыка +0.04% за 1 МС (макс. 32%)"),
        Buff(f"{S.LUNAR_BASE_INC}.lunar_bloom",
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_EM * _lauma_em(ctx)),
             target=TEAM,
             source="Nature's Chorus: +0.0175% базового урона лунных бутонов за 1 МС (макс. 14%)"),
    ),
    sources=(),
    constellations={
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(f"{S.FLAT_BASE_DMG}.lunar_bloom",
                     lambda ctx: C2_PALE_HYMN_LB * _lauma_em(ctx),
                     target=TEAM, requires=(PALE_HYMN,),
                     source="C2 Лаумы: Pale Hymn ещё +400% МС"),
                Buff("lunar_bonus.lunar_bloom", C2_LB_BONUS, target=TEAM,
                     source="C2 Лаумы: +40% урона лунных бутонов отряду"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            buffs=(Buff(f"{S.FLAT_BASE_DMG}.lunar_bloom",
                        lambda ctx: (PALE_HYMN_LB_C3 - PALE_HYMN_LB) * _lauma_em(ctx),
                        target=TEAM, requires=(PALE_HYMN,),
                        source="C3 Лаумы: Pale Hymn до 472.26% МС"),),
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(Buff("elevation.lunar_bloom", C6_ELEVATION, target=TEAM,
                        source="C6 Лаумы: +25% возвышения лунных бутонов"),),
        ),
    },
    note="Саппорт лунных бутонов (Moonsign).",
)

LAUMA_COMBO_DICT = {
    "hold_eq": with_rotation(
        LAUMA_KIT,
        sources=(
            elemental("Навык (удержание)", "em", HOLD_SKILL_EM, "dendro", "skill", [occ(1, ON)]),
            lunar_bloom("Навык (удержание) — лунные бутоны", "em", HOLD_SKILL_LB_EM,
                        [occ(1, ON)], kind="skill"),
            elemental("Frostgrove Sanctuary", "em", SANCTUARY_EM, "dendro", "skill",
                      [occ(SANCTUARY_HITS, OFF)]),
        ),
        constellation_sources={
            6: (lunar_bloom("C6: Frostgrove — лунные бутоны", "em", C6_SANCTUARY_LB_EM,
                            [occ(C6_SANCTUARY_LB_HITS, OFF)], kind="skill"),),
        },
    ),
}

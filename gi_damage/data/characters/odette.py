"""
Одетта — часть кита, НЕ зависящая от ротации/отряда.

Источники урона (в т.ч. по созвездиям) сюда не входят — подставляются
per-team через core.entities.with_rotation(), см. data/teams/*.py.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW
from ...core.sources import elemental, occ, stellar_swirl


def _odette_mp(stats) -> float:
    """Пассивка Одетты: множитель от атаки.

    MIN(АТК - 1000, 3000) * 0.015 / 100 + 1
    """
    return min(stats.atk - 1000.0, 3000.0) * 0.015 / 100.0 + 1.0


SPLENDOR_STACKS = 4          # стаков «Marvelous Splendor» с навыка (C0)
SPLENDOR_PER_STACK = 0.15    # +15% урона звёздного рассеивания за стак
SPLENDOR_C1_EXTRA = 2        # C1: ещё 2 стака при призыве двойника
SPLENDOR_C2_ATK = 0.07       # C2: +7% АТК за стак


def splendor_stacks(constellation: int) -> float:
    """Сколько стаков держится к моменту ударов."""
    return SPLENDOR_STACKS + (SPLENDOR_C1_EXTRA if constellation >= 1 else 0)


ODETTE_BURST_TIME = 1.5      # анимация, плоско добавляется ко времени ротации
SNOW_SWAN_BONUS = 0.50       # «Сон снежного лебедя»: +50% урона звёздных реакций
SNOW_SWAN_C4_SHARE = 0.50    # C4: половина эффекта достаётся остальному отряду


def odette_burst_buffs(constellation: int):
    """Баффы «Сна снежного лебедя» — только если взрыв применён."""
    out = [Buff(S.SSW_BONUS, SNOW_SWAN_BONUS, target=SELF,
                source="Сон снежного лебедя: +50% урона звёздных реакций")]
    if constellation >= 5:
        out = [Buff(S.SSW_BONUS, SNOW_SWAN_BONUS + 0.12, target=SELF,
                    source="Сон снежного лебедя: +62% урона звёздных реакций (C5)")]
        out.append(Buff(S.SSW_BONUS, (SNOW_SWAN_BONUS + 0.12) * SNOW_SWAN_C4_SHARE,
                        target=OTHERS, source="C5: половина «Сна снежного лебедя» отряду"))
        return tuple(out)

    if constellation == 4:
        out.append(Buff(S.SSW_BONUS, SNOW_SWAN_BONUS * SNOW_SWAN_C4_SHARE,
                        target=OTHERS, source="C4: половина «Сна снежного лебедя» отряду"))
    return tuple(out)


ODETTE_KIT = Character(
    name="Одетта",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 335.0,
        S.CRIT_VALUE: 0.6 + 0.384,
    },
    buffs=(
        Buff(S.SSW_BASE_INC, 0.14, target=TEAM,
             source="Одетта: +14% базового урона звёздного рассеивания"),
        # Пока Одетта на поле — стаки ещё у неё
        Buff(S.SSW_BONUS, SPLENDOR_STACKS * SPLENDOR_PER_STACK,
             target=SELF, requires=(ON,),
             source="Marvelous Splendor: 4 стака себе (на поле)"),
        # Ушла с поля — стаки перешли отряду
        Buff(S.SSW_BONUS, SPLENDOR_STACKS * SPLENDOR_PER_STACK,
             target=OTHERS,
             source="Marvelous Splendor: 4 стака отряду"),
    ),
    multipliers={"mp": _odette_mp},
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            # Доп. инстанс в конце «дуэта» после особого навыка — sources per-team.
            buffs=(
                # Усиление A4: при призыве двойника ещё 2 стака Splendor.
                Buff(S.SSW_BONUS, SPLENDOR_C1_EXTRA * SPLENDOR_PER_STACK,
                     target=SELF, requires=(ON,),
                     source="C1: +2 стака Splendor себе"),
                Buff(S.SSW_BONUS, SPLENDOR_C1_EXTRA * SPLENDOR_PER_STACK,
                     target=OTHERS,
                     source="C1: +2 стака Splendor отряду"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                # Каждый стак даёт ещё и +7% АТК. Количество стаков зависит
                # от C1, поэтому 6 = максимум (4 базовых + 2 от C1) — если
                # у вас в конкретном отряде C1 не взято, поправьте множитель.
                Buff(S.ATK_PCT, 6 * SPLENDOR_C2_ATK,
                     target=SELF, requires=(ON,),
                     source="C2: +7% АТК за стак (себе, на поле)"),
                Buff(S.ATK_PCT, 6 * SPLENDOR_C2_ATK,
                     target=OTHERS,
                     source="C2: +7% АТК за стак (отряду)"),
                # Пока на поле двойник — цель теряет 20% крио и анемо сопр.
                Buff("res_reduction.cryo", 0.20, target=TEAM,
                     source="C2: -20% крио сопротивления"),
                Buff("res_reduction.anemo", 0.20, target=TEAM,
                     source="C2: -20% анемо сопротивления"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Использование навыка (АТК)": lambda s: replace(s, mv=2.2967),
                "Навык (АТК), Plume Dance": lambda s: replace(s, mv=0.9146),
                "Навык (АТК), Wing Dance": lambda s: replace(s, mv=1.0936),
                "Навык — SSW, Plume Dance": lambda s: replace(s, mv=0.8612),
                "Навык — SSW, Wing Dance": lambda s: replace(s, mv=1.0299),
                "Особый навык — SSW": lambda s: replace(s, mv=9.7461),
            },
        ),
        4: Constellation(number=4, name="C4"),
        5: Constellation(number=5, name="C5"),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                # Стаки Splendor больше не расходуются: Одетта сохраняет их и
                # вне поля, то есть эффект работает у неё и у отряда одновременно.
                # Базовые баффы требуют ON, поэтому добавляем зеркальные на OFF.
                Buff(S.SSW_BONUS, 6 * SPLENDOR_PER_STACK,
                     target=SELF, requires=(OFF,),
                     source="C6: стаки Splendor не расходуются (бонус SSW вне поля)"),
                Buff(S.ATK_PCT, 6 * SPLENDOR_C2_ATK,
                     target=SELF, requires=(OFF,),
                     source="C6: стаки Splendor не расходуются (АТК вне поля)"),
                # «Elevated by» — это «Возвышение» из формулы, множитель
                # (1 + возвышение). +25% всем со стаками, ещё +20% самой Одетте.
                Buff("elevation.stellar_swirl", 0.25, target=TEAM,
                     source="C6: +25% возвышения урона SSW всем со стаками"),
                Buff("elevation.stellar_swirl", 0.20, target=SELF,
                     source="C6: +20% возвышения урона SSW самой Одетте"),
            ),
        ),
    },
)

ODETTE_BURST_SOURCES = (
    elemental("Взрыв — рассечения (АТК)", "atk", 1.9832, "cryo", "burst", [occ(3, ON)]),
    elemental("Взрыв — финальное рассечение (АТК)", "atk", 3.0649, "cryo", "burst", [occ(1, ON)]),
)

ODETTE_COMBO_DICT = {
    "odette_short_mizuki_combo_no_burst" : with_rotation(
    ODETTE_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.9454, "cryo", "skill",
                  [occ(1, ON,)]),
        elemental("Навык (АТК), Plume Dance", "atk", 0.7747, "cryo", "skill",
                  [occ(3, OFF,), occ(2, OFF, DREAM)]),
        elemental("Навык (АТК), Wing Dance", "atk", 0.9264, "cryo", "skill",
                  [occ(2, OFF,), occ(2, OFF, DREAM)]),
        
        stellar_swirl("Навык — SSW, Plume Dance", "atk", 0.7295, "cryo",
                      [occ(1, OFF, FROSTGLOW),occ(2, OFF, FROSTGLOW, INST),
                       occ(2, OFF, INST, DREAM, FROSTGLOW)], multipliers=("mp",)),
        stellar_swirl("Навык — SSW, Wing Dance", "atk", 0.8724, "cryo",
                      [occ(1, OFF, FROSTGLOW),occ(1, OFF, FROSTGLOW, INST),
                       occ(2, OFF, INST, DREAM, FROSTGLOW)], multipliers=("mp",)),
        stellar_swirl("Особый навык — SSW", "atk", 8.2555, "cryo",
                      [occ(1, ON, INST, FROSTGLOW)], multipliers=("mp",)),
    ),
    constellation_sources={
        1: (
            stellar_swirl("C1: доп. атака после особого навыка",
                          "atk", 4.50, "cryo",
                          [occ(1, ON, INST, FROSTGLOW)], multipliers=("mp",)),
        ),
        4: (
            stellar_swirl("C4: доп. атака",
                          "atk", 0.99, "cryo",
                          [occ(1, OFF,), occ(3, OFF, INST, DREAM, FROSTGLOW)], multipliers=("mp",)),
        ),
    },
),
    

}
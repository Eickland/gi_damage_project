"""
Отряд Мидзуки/Одетта/Крио ГГ/Сахароза,
Короткая ротация с 3 проками A4 мидзуки, Сахароза в инструкторе, Мидзуки в изумрудной тени
"""

from __future__ import annotations
from dataclasses import replace

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation
from ...core.sources import Occurrence, elemental, occ, stellar_swirl
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, FROSTGLOW,BREEZEBORNE

# =========================================================================== #
#  Мидзуки — анемо, main dps
# =========================================================================== #

SSW_EM_RATE = 0.045          # прирост урона SSW за 100 МС (базовый уровень)
SSW_EM_RATE_C3 = 0.054       # то же с C3
C6_EM_THRESHOLD = 500        # МС сверх этого порога конвертируется в крит
C6_RATE_PER_EM = 0.0004      # +0.04% крит. шанса за 1 МС, максимум +20%
C6_DMG_PER_EM = 0.0016       # +0.16% крит. урона за 1 МС, максимум +80%
C6_MAX_EXCESS = 500          # обе планки упираются ровно на 1000 МС

def _c6_crit_value(em: float) -> float:
    """Прибавка к крит-вэлью от C6. CV = 2*шанс + крит.урон."""
    excess = min(max(em - C6_EM_THRESHOLD, 0.0), C6_MAX_EXCESS)
    return (2 * C6_RATE_PER_EM + C6_DMG_PER_EM) * excess

MIZUKI = Character(
    
    name="Мидзуки",
    element="anemo",
    weapon_type="catalyst",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 215.0,
        S.BASE_EM: 115,
        S.CRIT_VALUE: 0.6
    },
    buffs=(
        Buff(S.EM_PCT, 0.10, target=SELF, source="Мидзуки A4"),
        
        # Талант: бонус урона звёздного рассеивания = 4.5% за каждые 100 МС Мидзуки.
        # Себе — считается по своему же МС в текущем окне.
        Buff(S.SSW_BONUS,
             lambda ctx: 0.045 * ctx.own("em") / 100.0,
             target=SELF, requires=(ON,),
             source="Мидзуки: 4.5% урона SSW за 100 МС (себе)"),
        
        # Отряду — по МС Мидзуки на поле, в том же окне Инструктора.
        Buff(S.SSW_BONUS,
             lambda ctx: 0.045 * ctx.stat("Мидзуки", "em",
                                          ctx.mirror(ON, keep=[INST])) / 100.0,
             target=OTHERS, requires=(OFF,),
             source="Мидзуки: 4.5% урона SSW за 100 МС (отряду)"),

        # Отряду: +10% от «голого» МС Мидзуки, пока она на поле.
        Buff(S.BASE_EM,
             lambda ctx: 0.10 * ctx.stat("Мидзуки", S.BASE_EM,
                                         ctx.mirror(ON, keep=[INST])),
             target=OTHERS, requires=(OFF,),
             source="Мидзуки A4"),
    ),
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.0394, "anemo", "skill",
                  [occ(1, ON, DREAM)]),
        elemental("Навык (АТК)", "atk", 0.8084, "anemo", "skill",
                  [occ(12, ON, DREAM)]),
        elemental("Использование взрыва (АТК)", "atk", 1.6934, "anemo", "burst",
                  [occ(1, ON, DREAM)]),
        elemental("Взрыв (АТК)", "atk", 1.2701, "anemo", "burst",
                  [occ(8, ON, DREAM)]),
        elemental("Перья (МС)", "em", 10.0, "anemo", "skill",
                  [occ(1, ON, DREAM), occ(2, ON, INST, DREAM),occ(1, ON)],
                  note="«Quills EM MV%» = 1000%"),
        stellar_swirl("Навык — звёздное рассеивание (МС)", "em", 10.0, "anemo",
                      [occ(1, ON, DREAM, BREEZEBORNE, FROSTGLOW), occ(2, ON, INST, DREAM, FROSTGLOW, BREEZEBORNE),occ(1, ON, BREEZEBORNE, FROSTGLOW)],
                      note="«Skill EM SSW MV%» = 1000%"),
    ),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            sources=(
                stellar_swirl("C1: доп. звёздное рассеивание (МС)", "em", 4.0,
                              "anemo", [occ(1, ON, DREAM), occ(2, ON, INST, DREAM)]),
                elemental("C1: доп. базовый урон", "em", 5.5, "anemo", "skill",
                          [occ(1, ON, DREAM, BREEZEBORNE, FROSTGLOW), occ(2, ON, INST, DREAM, BREEZEBORNE, FROSTGLOW)]),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=tuple(
                Buff(f"dmg_bonus.{element}",
                     lambda ctx: 0.0004 * ctx.stat("Мидзуки", "em",
                                                   ctx.mirror(ON, keep=[INST, DREAM])),
                     target=TEAM, requires=(DREAM,), temporary=True,
                     source=f"C2 Мидзуки: +0.04% {element} урона за 1 МС")
                for element in ("pyro", "hydro", "cryo", "electro")
            ) + tuple(
                Buff(f"res_reduction.{element}", 0.20,
                     target=TEAM, requires=(DREAM,), temporary=True,
                     source=f"C2 Мидзуки: -20% сопротивления к {element}")
                for element in ("pyro", "hydro", "cryo", "electro", "anemo")
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            # +3 уровня таланта элементального навыка -> новые множители
            patches={
                "Использование навыка (АТК)": lambda s: replace(s, mv=1.2271),
                "Навык (АТК)":                lambda s: replace(s, mv=0.9544),
            },
            # Талант «за 100 МС» усиливается с 4.5% до 5.4%. Базовый бафф никуда
            # не девается, поэтому добавляем ДЕЛЬТУ (баффы складываются).
            buffs=(
                Buff(S.SSW_BONUS,
                    lambda ctx: (SSW_EM_RATE_C3 - SSW_EM_RATE) * ctx.own("em") / 100.0,
                    target=SELF, requires=(ON,),
                    source="C3: SSW за 100 МС 4.5% -> 5.4% (себе)"),
                Buff(S.SSW_BONUS,
                    lambda ctx: (SSW_EM_RATE_C3 - SSW_EM_RATE)
                                * ctx.stat("Мидзуки", "em",
                                            ctx.mirror(ON, keep=[INST])) / 100.0,
                    target=OTHERS, requires=(OFF,),
                    source="C3: SSW за 100 МС 4.5% -> 5.4% (отряду)"),
            ),
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                # Внутри Дрейфа грёз весь урон звёздного рассеивания отряда
                # получает +10% крит. шанса и +20% крит. урона.
                # В крит-вэлью это 2*0.10 + 0.20 = 0.40.
                Buff("crit_value.stellar_swirl", 2 * 0.10 + 0.20,
                    target=TEAM, requires=(DREAM,), temporary=True,
                    source="C6: крит по урону SSW (+10% шанс, +20% урон)"),

                # МС сверх 500 конвертируется в крит самой Мидзуки.
                Buff(S.CRIT_VALUE,
                    lambda ctx: _c6_crit_value(ctx.own("em")),
                    target=SELF,
                    source="C6: МС сверх 500 -> крит (до +20% шанса, +80% урона)"),
            ),
        ),
    },
    note="Анемо, main dps",
)

# =========================================================================== #
#  Крио ГГ (Крио Путешественник)                                              #
# =========================================================================== #
CRYO_MC = Character(
    name="Крио ГГ",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 212.0+7+3,
        S.BASE_EM: 160+15+60,
        S.CRIT_VALUE: 0.6+0.2+0.2,
        S.ATK_PCT: 0.2+0.24
    },
    buffs = (Buff(S.SSW_BASE_INC, 0.07, target=TEAM,
                     source="A3 Крио ГГ"),),
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON,)]),
        elemental("Навык (АТК)", "atk",0.3851, "cryo", "skill",
                  [occ(5, OFF, DREAM),occ(3, OFF)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST)], kind="burst"),
    ),
    constellations={
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.BASE_EM, 120.0, target=TEAM, requires=(ON,),
                source="+120 МС активному персонажу"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Взрыв — SSW": lambda s: replace(s, mv=(1.1715 + 8 * 0.0586)),
            },
        ),
        5: Constellation(
            number=5,
            name="C5",
            patches={
                "Использование навыка (АТК)": lambda s: replace(s, mv=1.9482),
                "Навык (АТК)": lambda s: replace(s, mv=0.4546),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                temp(S.SSW_BONUS, 0.4, FROSTGLOW, target=TEAM,
                        source="+40% к урону звездных реакций на 15с после применения взрыва стихий"),
                    ),
        ),
    },
    note="",
)


# =========================================================================== #
#  Одетта                                                                     #
# =========================================================================== #
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

ODETTE_BURST_SOURCES = (
    elemental("Взрыв — рассечения (АТК)", "atk", 1.9832, "cryo", "burst", [occ(3, ON)]),
    elemental("Взрыв — финальное рассечение (АТК)", "atk", 3.0649, "cryo", "burst", [occ(1, ON)]),
)


def odette_burst_buffs(constellation: int):
    """Баффы «Сна снежного лебедя» — только если взрыв применён."""
    out = [Buff(S.SSW_BONUS, SNOW_SWAN_BONUS, target=SELF,
                source="Сон снежного лебедя: +50% урона звёздных реакций")]
    if constellation >= 5:

        out = [Buff(S.SSW_BONUS, SNOW_SWAN_BONUS + 0.12, target=SELF,
                    source="Сон снежного лебедя: +62% урона звёздных реакций (C5)")]
        out.append(Buff(S.SSW_BONUS, (SNOW_SWAN_BONUS+0.12) * SNOW_SWAN_C4_SHARE,
                        target=OTHERS, source="C5: половина «Сна снежного лебедя» отряду"))
        return tuple(out)    

    if constellation == 4:
        out.append(Buff(S.SSW_BONUS, SNOW_SWAN_BONUS * SNOW_SWAN_C4_SHARE,
                        target=OTHERS, source="C4: половина «Сна снежного лебедя» отряду"))
    return tuple(out)

ODETTE = Character(
    name="Одетта",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 335.0,
        S.CRIT_VALUE: 0.6+0.384,
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
             source="Marvelous Splendor: 4 стака отряду")
    ),
    multipliers={"mp": _odette_mp},
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.9454, "cryo", "skill",
                  [occ(1, OFF,)]),
        elemental("Навык (АТК), Plume Dance", "atk", 0.7747, "cryo", "skill",
                  [occ(2, OFF,),occ(3, OFF, DREAM)]),
        elemental("Навык (АТК), Wing Dance", "atk", 0.9264, "cryo", "skill",
                  [occ(1, OFF,),occ(3, OFF, DREAM)]),
        stellar_swirl("Навык — SSW, Plume Dance", "atk", 0.7295, "cryo",
                      [occ(1, OFF,), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE),occ(2, OFF,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
        stellar_swirl("Навык — SSW, Wing Dance", "atk", 0.8724, "cryo",
                      [occ(1, OFF,), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE),occ(1, OFF,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
        stellar_swirl("Особый навык — SSW", "atk", 8.2555, "cryo",
                      [occ(1, ON, INST,FROSTGLOW)], multipliers=("mp",)),
    ),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            # Доп. инстанс в конце «дуэта» после особого навыка.
            # В режиме Radiance: Stellar Swirl — 450% от атаки Одетты.
            sources=(
                stellar_swirl("C1: доп. атака после особого навыка",
                              "atk", 4.50, "cryo",
                              [occ(1, ON, INST,FROSTGLOW)], multipliers=("mp",)),
            ),
            # Усиление A4: при призыве двойника ещё 2 стака Splendor.
            buffs=(
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
                # Каждый стак даёт ещё и +7% АТК.
                # Количество стаков зависит от C1 — поэтому читаем созвездие.
                Buff(S.ATK_PCT,
                     6 * SPLENDOR_C2_ATK,
                     target=SELF, requires=(ON,),
                     source="C2: +7% АТК за стак (себе, на поле)"),
                Buff(S.ATK_PCT,
                     6 * SPLENDOR_C2_ATK,
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
        4: Constellation(
            number=4,
            name="C4",
            sources=(
                stellar_swirl("C4: доп. атака",
                              "atk", 0.99, "cryo",
                              [occ(1, OFF,), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE),occ(1, OFF,DREAM,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
            ),
        ),
        5: Constellation(
            number=5,
            name="C5",
        ),         
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                # Стаки Splendor больше не расходуются: Одетта сохраняет их и вне
                # поля, то есть эффект работает у неё и у отряда одновременно.
                # Базовые баффы требуют ON, поэтому добавляем зеркальные на OFF.
                Buff(S.SSW_BONUS,
                    6 * SPLENDOR_PER_STACK,
                    target=SELF, requires=(OFF,),
                    source="C6: стаки Splendor не расходуются (бонус SSW вне поля)"),
                # То же для прибавки атаки от C2 — на C6 оно активно всегда.
                Buff(S.ATK_PCT,
                    6 * SPLENDOR_C2_ATK,
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

# =========================================================================== #
#  Фарузан                                                                   #
# =========================================================================== #
FARUZAN = Character(
    name="Фарузан",
    element="anemo",
    weapon_type="bow",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 196.0,
        S.CRIT_VALUE: 0.6,
        S.ATK_PCT: 0.24,
    },
    buffs = (Buff("crit_value.anemo", 0.4, target=TEAM,
                     source="С6 Фарузан, +40% анемо крит урона"),
             Buff("res_reduction.anemo", 0.30, target=TEAM,
                    source="Взрыв стихии: -30% анемо сопротивления")),
    sources=(),
    note="",
)


ALL = {c.name: c for c in (MIZUKI, CRYO_MC, ODETTE, FARUZAN)}

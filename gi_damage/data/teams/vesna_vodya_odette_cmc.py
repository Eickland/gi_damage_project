"""
Отряд Весна/Одетта/Крио ГГ/Водяница,
"""

from __future__ import annotations
from dataclasses import replace

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation
from ...core.sources import Occurrence, elemental, occ, stellar_swirl
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, FROSTGLOW,BREEZEBORNE, VODYA_LEAD, VODYA_CHORUS, TTDS_HALF,ARMED, DA1, DA2, DA3, DA4, DA5, DA6

# =========================================================================== #
#  Весна — анемо, main dps (меч)
# =========================================================================== #

DA_STACK = "vesna_da_stacks"

VESNA = Character(
    name="Весна",
    element="anemo",
    weapon_type="sword",
    default_field=ON,
    crit_mode="balance",

    stats={
        S.BASE_ATK: 354.0,
        S.CRIT_VALUE: 0.6+0.384,
        S.ATK_PCT: 0.24
    },
    buffs = (Buff(S.SSW_BASE_INC, 0.14, target=TEAM, source="A3 Весна"),
        *(Buff(DA_STACK, n, target=SELF, requires=(tag,),
               source=f"Disciplinary Action: da={n}")
          for n, tag in enumerate((DA1, DA2, DA3, DA4, DA5, DA6), start=1)),),
    multipliers={
        "disciplinary_action": lambda stats: 1.0 + 0.10 * stats.get(DA_STACK, 0.0),
    },
    sources=(
        elemental("Использование навыка", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON, TTDS_HALF)]),

        elemental("Windborne Sword Lv1", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON, ARMED, TTDS_HALF)],
                  extra_tags=("windborne_sword",)),

        elemental("Windborne Sword Lv2", "atk", 1.08, "anemo", "skill",
                  [occ(1, ON, ARMED, TTDS_HALF)],
                  extra_tags=("windborne_sword",)),

        stellar_swirl("Windborne Sword Lv2 — Spirit Blade", "atk", 2.016,
                  "anemo",[occ(1, ON, ARMED, DA1, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF)],"skill",
                  extra_tags=("spirit_blade",),
                  multipliers=("disciplinary_action",)),

        stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4", "atk", 0.8064,
                  "anemo",
                  [occ(4, ON, ARMED, DA2, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF), occ(4, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF), occ(4, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF)], "skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
        stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit", "atk",
                  2.8224, "anemo", 
                  [occ(1, ON, ARMED, DA2, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF), occ(1, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF), occ(1, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF)],"skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),

        elemental("Перо ветра", "atk", 0.1872, "anemo", "skill",
                  [occ(8, ON, ARMED, TTDS_HALF)]),

        stellar_swirl("Взрыв — Клинок Духа", "atk", 4.7376, "anemo",
                  [occ(1, ON, ARMED, DA3, BREEZEBORNE, FROSTGLOW, VODYA_LEAD, TTDS_HALF)], "burst",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
    ),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            sources = (
            stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4, C1", "atk", 0.8064,
                        "anemo",
                        [occ(4, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF)], "skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
            stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit, C1", "atk",
                        2.8224, "anemo", 
                        [occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF)],"skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),                
            ),
            buffs=(
                Buff(S.SSW_BONUS, 0.2,
                     target=SELF, requires=(ON,),
                     source="C1"),
            ),

        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.ATK_PCT, 0.4,
                     target=SELF, requires=(ON,),
                     source="C2"),
            ),
            patches={
                "Windborne Sword Lv2 — Spirit Blade": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF, VODYA_LEAD)]),
                "Windborne Sword Lv3 — Spirit Blade x4": lambda s: replace(s, occurrences=[occ(12, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF, VODYA_LEAD)]),
                "Windborne Sword Lv3 Spirit Blade Final Hit": lambda s: replace(s, occurrences=[occ(3, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF, VODYA_LEAD)]),
                "Взрыв — Клинок Духа": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF, VODYA_LEAD)]),
            },
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Windborne Sword Lv2 — Spirit Blade": lambda s: replace(s, mv=2.38),
                "Windborne Sword Lv3 — Spirit Blade x4": lambda s: replace(s, mv=0.952),
                "Windborne Sword Lv3 — Spirit Blade x4, C1": lambda s: replace(s, mv=0.952),
                "Windborne Sword Lv3 Spirit Blade Final Hit": lambda s: replace(s, mv=3.32),
                "Windborne Sword Lv3 Spirit Blade Final Hit, C1": lambda s: replace(s, mv=3.32),
            },
        ),
        4: Constellation(
            number=4,
            name="C4",
            buffs=(
                Buff(S.ATK_PCT, 0.48,
                     target=SELF, requires=(ON,),
                     source="C4"),
            ),
        ),
        5: Constellation(
            number=5,
            name="C5",
            patches={
                "Взрыв — Клинок Духа": lambda s: replace(s, mv=5.593),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("elevation.stellar_swirl", 0.2, target=SELF,
                    source="C6: +20% возвышения урона SSW самой Весны"),
            ),
            sources=(
                elemental("C6: Windborne Sword: Transpose", "atk", 1.50,
                          "anemo", "skill", [occ(4, ON, ARMED, BREEZEBORNE, FROSTGLOW, TTDS_HALF)],
                          extra_tags=("transpose",)),
                stellar_swirl("C6: Windborne Sword: Transpose — Клинок Духа",
                          "atk", 2.00, "anemo", 
                          [occ(4, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW, TTDS_HALF)],"skill",
                          extra_tags=("spirit_blade",
                                      "transpose"),multipliers=("disciplinary_action",)),
            ),
        ),
    },
    note="Анемо, меч, main dps..",
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
                "Взрыв — SSW": lambda s: replace(s, mv=(1.1715 + 8 * 0.0586) * 5),
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
                      [occ(1, OFF, TTDS_HALF), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE,VODYA_CHORUS, TTDS_HALF),occ(2, OFF,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
        stellar_swirl("Навык — SSW, Wing Dance", "atk", 0.8724, "cryo",
                      [occ(1, OFF, TTDS_HALF), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE,VODYA_CHORUS, TTDS_HALF),occ(1, OFF,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
        stellar_swirl("Особый навык — SSW", "atk", 8.2555, "cryo",
                      [occ(1, ON, INST,FROSTGLOW, TTDS_HALF)], multipliers=("mp",)),
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
                              [occ(1, ON, INST,FROSTGLOW, TTDS_HALF)], multipliers=("mp",)),
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
                              [occ(1, OFF, TTDS_HALF), occ(2, OFF, INST,DREAM,FROSTGLOW,BREEZEBORNE, TTDS_HALF),occ(1, OFF,DREAM,FROSTGLOW,BREEZEBORNE)], multipliers=("mp",)),
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

def vodyanitsa_stack_bonus(max_hp: float) -> float:
    """+260 доп. базового урона за каждую 1000 Max HP Водяницы свыше 40000,
    максимум 6500 (A4 «Dirge of the Fandyr»)."""
    return min(260.0 * max(0.0, max_hp - 40000.0) / 1000.0, 6500.0)

def vodyanitsa_c1_bonus(max_hp: float) -> float:
    return 0.008*max_hp
 
 
VODYANITSA = Character(
    name="Водяница",
    element="hydro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_HP: 14818.0,
        S.CRIT_VALUE: 0.6,
        S.HP_PCT: 0.288
    },
    buffs=(Buff(S.FLAT_BASE_DMG, lambda ctx: vodyanitsa_stack_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
         target="Весна", requires=(VODYA_LEAD,),
         source="Водяница: Lead Vocal (SSW навыка)"),
            Buff(S.FLAT_BASE_DMG, lambda ctx: vodyanitsa_stack_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
         target="Крио ГГ", requires=(VODYA_CHORUS,),
         source="Водяница: Chorus (SSW навыка)"),
        Buff("res_reduction.anemo", 0.35, target=TEAM,
                    source="-35% анемо сопротивления"),
        Buff("res_reduction.cryo", 0.3, target=TEAM,
                    source="-30% крио сопротивления"),
        Buff("res_reduction.hydro", 0.3, target=TEAM,
                    source="-30% гидро сопротивления"),
        Buff("res_reduction.anemo", -1000, target=SELF,
                    source="Нет вклада в звездные реакции"),
        Buff("res_reduction.cryo", -1000, target=SELF,
                    source="Нет вклада в звездные реакции")),
    
    sources=(elemental("Использование навыка", "hp", 0.589, "hydro", "skill",
                  [occ(1, ON,)]),
        elemental("Навык, Horn of Spring", "hp", 0.589, "hydro", "skill",
                  [occ(5, OFF,),]),),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff(S.FLAT_ATK, lambda ctx: vodyanitsa_c1_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
                     target=OTHERS,
                     source="C1"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff("crit_value.stellar_swirl",
                     0.6,
                     target=OTHERS, requires=(ON,),
                     source="C2: +60% К криту урону звездного рассеивания"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            buffs=(Buff("res_reduction.cryo", 0.054, target=TEAM,
                    source="C3: Бонус к срезу крио сопротивления"),
            Buff("res_reduction.hydro", 0.054, target=TEAM,
                    source="C3: Бонус к срезу сопротивления")
            ),
        ),
        4: Constellation(
            number=4,
            name="C4",
            buffs=(Buff(S.HP_PCT, 0.6, target=SELF,
                    source="C4: Бонус к хп"),
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
                Buff("elevation.stellar_swirl", 0.25, target=TEAM,
                    source="C6: +25% возвышения урона SSW всем"),
                Buff("crit_value.stellar_swirl",0.6,
                     target=OTHERS, requires=(OFF,),
                     source="C6: +60% К криту урону звездного рассеивания"),
            ),
        ),
    },
    note="",
)


ALL = {c.name: c for c in (VESNA, CRYO_MC, ODETTE, VODYANITSA)}

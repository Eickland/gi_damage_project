"""
Оружие.

"""

from __future__ import annotations

from ..core.buffs import SELF, Buff, TEAM, temp
from ..core.entities import Weapon
from ..core.stats import S
from .tags import BREEZEBORNE, TTDS_HALF, ON

# --------------------------------------------------------------------------- #
WANDERER_SONG = Weapon(
    name="Песнь странника",
    base_atk=510.0,
    stats={S.CRIT_VALUE: 0.551},
    refinement=5,
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.20,
            S.BASE_EM: 80.0,
            "dmg_bonus.anemo": 0.16,
        },
    },
    note="Усредненный бонус за 6 ротаций",
)

SAC_JADE = Weapon(
    name="Sacrificial Jade",
    base_atk=454.0,
    stats={S.CRIT_VALUE: 0.368*2},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 40,
        },
        2: {
            S.BASE_EM: 50,
        },
        3: {
            S.BASE_EM: 60,
        },
        4: {
            S.BASE_EM: 70,
        },
        5: {
            S.BASE_EM: 80,
        },
    },
    note="",
)

SUNNY_MORNING_SLEEP_IN = Weapon(
    name="Сон солнечным утром",
    base_atk=542.0,
    stats={S.BASE_EM: 265},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 248.0,
        },
        5: {
            S.BASE_EM: 248.0*2,
        },
    },
    note="",
)

STARCALLERS_WATCH = Weapon(
    name="Starcaller's Watch",
    base_atk=542.0,
    stats={S.BASE_EM: 265},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 100.0,
        },
    },
    note="",
)

RELIQUARY_OF_TRUTH = Weapon(
    name="Reliquary of Truth",
    base_atk=542.0,
    stats={S.CRIT_VALUE: 0.882},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 80,
            S.CRIT_VALUE: 0.16
        },
    },
    note="",
)

DAWNING_FROST = Weapon(
    name="Dawning Frost",
    base_atk=510.0,
    stats={S.CRIT_VALUE: 0.551},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 72+48,
        },
        2: {
            S.BASE_EM: 90+60,
        },
        3: {
            S.BASE_EM: 108+72,
        },
        4: {
            S.BASE_EM: 126+84,
        },
        5: {
            S.BASE_EM: 144+96,
        },
    },
    note="",
)

EXAIPHANES = Weapon(
    name="Пробуждение",
    base_atk=608.0,
    stats={S.CRIT_VALUE: 0.331*2+0.42},
    refinement=3,
    stats_by_refinement={
        3: {
            S.ATK_PCT: 0.24,
        },
    },
    note="Сигна Крио ГГ.",
)

SILVER_LIGHT = Weapon(
    name="Серебряный свет",
    base_atk=510.0,
    refinement=5,
    stats={S.ATK_PCT: 0.413},
    stats_by_refinement={
        5: {
            S.BASE_EM: 208,
        },
    },
    note="Ивентовое оружие",
)

EMBERWELL = Weapon(
    name="Источник пламени",
    base_atk=510.0,
    refinement=5,
    stats={S.BASE_EM: 165},
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.32,
            S.SSW_BONUS: 0.32,
        },
    },
    note="Крафтовое оружие из снежной",
)

TTDS_BONUS_HALF = {r: 0.12 + 0.06 * (r - 1) for r in range(1, 6)}

TTDS_HALF_CATALYSATOR = Weapon(
    name="Эпос",
    base_atk=401.0,
    refinement=5,
    stats={S.HP_PCT: 0.352},
    buffs_by_refinement={
        r: (temp(S.ATK_PCT, TTDS_BONUS_HALF[r], requires=(TTDS_HALF,), target=TEAM,
                 source=f"Эпос R{r}: +{TTDS_BONUS_HALF[r]:.0%} "
                        f"атаки персонажу"),)
        for r in TTDS_BONUS_HALF
    },
    note="",
)

MAELSTROM_BONUS = {r:((0.08+0.02*r)*3)*1.75 for r in range(1, 6)}

MAELSTROM = Weapon(
    name="Ода водоворота",
    base_atk=542.0,
    refinement=1,
    stats={S.HP_PCT: 0.662},
    buffs_by_refinement={
        r: (temp(S.ATK_PCT, MAELSTROM_BONUS[r], requires=(ON,), target=TEAM,
                 source=f"Ода водоворота R{r}: +{MAELSTROM_BONUS[r]:.0%} "
                        f"атаки активному персонажу"),)
        for r in MAELSTROM_BONUS
    },
    stats_by_refinement={
        1: {
            S.HP_PCT: (0.04*3)*1.75,
        },
        2: {
            S.HP_PCT: (0.05*3)*1.75,
        },
        3: {
            S.HP_PCT: (0.06*3)*1.75,
        },
        4: {
            S.HP_PCT: (0.07*3)*1.75,
        },
        5: {
            S.HP_PCT: (0.08*3)*1.75,
        },
    },
    note="Сигна Водяницы",
)

FINALE = Weapon(
    name="Финал глубин",
    base_atk=565.0,
    refinement=5,
    stats={S.ATK_PCT: 0.276},
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.24,
        },
    },
    note="Без лечения",
)

HARBINGER = Weapon(
    name="Предвестник",
    base_atk=401.0,
    refinement=5,
    stats={S.CRIT_VALUE: 0.469},
    stats_by_refinement={
        5: {
            S.CRIT_VALUE: 0.28*2,
        },
    },
    note="Хп больше 90%",
)

BOUGH = Weapon(
    name="Новая ветвь",
    base_atk=510.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.551},
    stats_by_refinement={
        1: {
            S.ATK_PCT: 0.06*3,
            S.SSW_BONUS: 0.08*3,
        },
        2: {
            S.ATK_PCT: 0.075*3,
            S.SSW_BONUS: 0.1*3,
        },
        3: {
            S.ATK_PCT: 0.09*3,
            S.SSW_BONUS: 0.12*3,
        },
        4: {
            S.ATK_PCT: 0.105*3,
            S.SSW_BONUS: 0.14*3,
        },
        5: {
            S.ATK_PCT: 0.12*3,
            S.SSW_BONUS: 0.16*3,
        },
    },
    note="Оружие из баннера",
)

LOW_BASE_CRIT_STATSTICK = Weapon(
    name="Крит затычка с низкой базой",
    base_atk=542.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.882},
    note="",
)

MID_BASE_CRIT_STATSTICK = Weapon(
    name="Крит затычка с средней базой",
    base_atk=608.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.662},
    note="",
)

HIGH_BASE_CRIT_STATSTICK = Weapon(
    name="Крит затычка с высокой базой",
    base_atk=674.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.441},
    note="",
)

AZURELIGHT = Weapon(
    name="Лазурное сияние",
    base_atk=674.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.441},
    stats_by_refinement={
        1: {
            S.ATK_PCT: 0.24,
        },
    },
    note="",
)

FROSTFEATHER = Weapon(
    name="Морозное перо белого озера",
    base_atk=674.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.221*2},
    stats_by_refinement={
        1: {
            S.ATK_PCT: 0.08*3,
            S.CRIT_VALUE: 0.5
        },
        2: {
            S.ATK_PCT: 0.1*3,
            S.CRIT_VALUE: 0.65
        },
        3: {
            S.ATK_PCT: 0.12*3,
            S.CRIT_VALUE: 0.8
        },
        4: {
            S.ATK_PCT: 0.14*3,
            S.CRIT_VALUE: 0.95
        },
        5: {
            S.ATK_PCT: 0.16*3,
            S.CRIT_VALUE: 1.1
        },
    },
    note="Сигнатурное оружие Одетты",
)

CHRYSALIS = Weapon(
    name="За пределами кокона",
    base_atk=674.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.221*2},
    stats_by_refinement={
        1: {
            S.SSW_BONUS: 0.36,
            S.CRIT_VALUE: 0.56
        },
        2: {
            S.SSW_BONUS: 0.45,
            S.CRIT_VALUE: 0.72
        },
        3: {
            S.SSW_BONUS: 0.54,
            S.CRIT_VALUE: 0.88
        },
        4: {
            S.SSW_BONUS: 0.63,
            S.CRIT_VALUE: 1.4
        },
        5: {
            S.SSW_BONUS: 0.72,
            S.CRIT_VALUE: 1.20
        },
    },
    note="Сигнатурное оружие Весны",
)

CEREMONIAL = Weapon(
    name="Церемон",
    base_atk=454.0,
    stats={S.BASE_EM: 221},
    refinement=5,
    note="",
)

FAV_BOW = Weapon(
    name="Лук фавония",
    base_atk=454.0,
    refinement=5,
    note="",
)

#: Бонус урона звёздных реакций по рангу пробуждения (24% на R1, +6% за ранг).
BREEZEBORNE_BONUS = {r: 0.24 + 0.06 * (r - 1) for r in range(1, 6)}

BREEZEBORNE_BOW = Weapon(
    name="Напевы ветра",
    base_atk=510.0,
    refinement=1,
    stats={
        S.CRIT_VALUE: 2 * 0.276,
    },
    buffs_by_refinement={
        r: (temp(S.SSW_BONUS, BREEZEBORNE_BONUS[r], BREEZEBORNE, target=TEAM,
                 source=f"Напевы ветра R{r}: +{BREEZEBORNE_BONUS[r]:.0%} "
                        f"урона звёздных реакций отряду"),)
        for r in BREEZEBORNE_BONUS
    },
)

ALL = {w.name: w for w in (WANDERER_SONG, SUNNY_MORNING_SLEEP_IN, EXAIPHANES,
                           SILVER_LIGHT, CEREMONIAL,FAV_BOW)}

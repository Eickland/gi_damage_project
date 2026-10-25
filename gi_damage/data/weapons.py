"""
Оружие.

"""

from __future__ import annotations

from ..core.buffs import SELF, Buff, TEAM, temp, OTHERS
from ..core.entities import Weapon
from ..core.stats import S
from .tags import BREEZEBORNE, TTDS_HALF, ON,TTDS_FULL, ELEGY

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

#: Та же «Песнь странника», но элементальный бонус пассивки — электро
#: (для Яэ Мико). Значения те же, что у WANDERER_SONG.
WANDERER_SONG_ELECTRO = Weapon(
    name="Песнь странника",
    base_atk=510.0,
    stats={S.CRIT_VALUE: 0.551},
    refinement=5,
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.20,
            S.BASE_EM: 80.0,
            "dmg_bonus.electro": 0.16,
        },
    },
    note="Усредненный бонус за 6 ротаций, элементальный бонус — электро",
)

#: «Песнь странника» с крио элементальным бонусом (для Ризли).
WANDERER_SONG_CRYO = Weapon(
    name="Песнь странника",
    base_atk=510.0,
    stats={S.CRIT_VALUE: 0.551},
    refinement=5,
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.20,
            S.BASE_EM: 80.0,
            "dmg_bonus.cryo": 0.16,
        },
    },
    note="Усредненный бонус за 6 ротаций, элементальный бонус — крио",
)

WINTER = Weapon(
    name="Застывшее сердце зимы",
    base_atk=510.0,
    stats={S.CRIT_VALUE: 0.551},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 40.0,
            S.SSW_BONUS: 0.12
        },
        2: {
            S.BASE_EM: 50.0,
            S.SSW_BONUS: 0.15
        },
        3: {
            S.BASE_EM: 60.0,
            S.SSW_BONUS: 0.18
        },
        4: {
            S.BASE_EM: 70.0,
            S.SSW_BONUS: 0.21
        },
        5: {
            S.BASE_EM: 80.0,
            S.SSW_BONUS: 0.24
        },
    },
    note="",
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
        2: {
            S.BASE_EM: 248.0*1.25,
        },
        3: {
            S.BASE_EM: 248.0*1.5,
        },
        4: {
            S.BASE_EM: 248.0*1.75,
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

STARSEALED = Weapon(
    name="Starsealed Edict",
    base_atk=542.0,
    stats={S.CRIT_VALUE: 0.882},
    refinement=1,
    stats_by_refinement={
        1: {
            S.BASE_EM: 48+72,
            S.CRIT_VALUE: 0.24
        },
        2: {
            S.BASE_EM: (48+72)*1.25,
            S.CRIT_VALUE: 0.24*1.25
        },
        3: {
            S.BASE_EM: (48+72)*1.5,
            S.CRIT_VALUE: 0.24*1.5
        },
        4: {
            S.BASE_EM: (48+72)*1.75,
            S.CRIT_VALUE: 0.24*1.75
        },
        5: {
            S.BASE_EM: (48+72)*2,
            S.CRIT_VALUE: 0.24*2
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
TTDS_BONUS_FULL = {r: 0.24 + 0.12 * (r - 1) for r in range(1, 6)}

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

TTDS_FULL_CATALYSATOR = Weapon(
    name="Эпос",
    base_atk=401.0,
    refinement=5,
    stats={S.HP_PCT: 0.352},
    buffs_by_refinement={
        r: (temp(S.ATK_PCT, TTDS_BONUS_FULL[r], requires=(TTDS_FULL,), target=TEAM,
                 source=f"Эпос R{r}: +{TTDS_BONUS_FULL[r]:.0%} "
                        f"атаки персонажу"),)
        for r in TTDS_BONUS_FULL
    },
    note="",
)

SYMPHONIST_BONUS = {r: 0.32 + 0.08* (r-1) for r in range(1,6)}

SYMPHONIST = Weapon(
    name="Симфонист ароматов",
    base_atk=608.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.662},
    buffs_by_refinement={
        r: (temp(S.ATK_PCT, SYMPHONIST_BONUS[r], requires=(ON,), target=TEAM,
                 source=f"Симфонист R{r}: +{SYMPHONIST_BONUS[r]:.0%} "
                        f"атаки персонажу"),)
        for r in SYMPHONIST_BONUS
    },
    stats_by_refinement={
        1: {
            S.ATK_PCT: 0.24+0.32,
        },
        2: {
            S.ATK_PCT: 0.3+0.4,
        },
        3: {
            S.ATK_PCT: 0.36+0.48,
        },
        4: {
            S.ATK_PCT: 0.42+0.56,
        },
        5: {
            S.ATK_PCT: 0.48+0.64,
        },
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

SLINGSHOT = Weapon(
    name="Рогатка",
    base_atk=401.0,
    refinement=5,
    stats={S.CRIT_VALUE: 0.312*2},
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
            S.CRIT_VALUE: 1.04
        },
        5: {
            S.SSW_BONUS: 0.72,
            S.CRIT_VALUE: 1.20
        },
    },
    note="Сигнатурное оружие Весны",
)

SACFRAG = Weapon(
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

FAV_SWORD = Weapon(
    name="Меч фавония",
    base_atk=454.0,
    refinement=5,
    note="",
)

FAV_LANCE = Weapon(
    name="Копье фавония",
    base_atk=454.0,
    refinement=5,
    note="",
)

TIDAL_SHADOW = Weapon(
    name="Тень волны",
    base_atk=510.0,
    refinement=5,
    stats={S.ATK_PCT: 0.413},
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.48,
        },
    },
    note="",
)

SERPENT_SPINE = Weapon(
    name="Меч драконьей кости",
    base_atk=510.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.276*2},
    stats_by_refinement={
        1: {
            "dmg_bonus.cryo": 0.3,
        },
    },
    note="",
)

FLOWER = Weapon(
    name="Цветок в латах",
    base_atk=565.0,
    refinement=5,
    stats={S.BASE_EM: 0.110},
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.24,
            S.BASE_EM: 96
        },
    },
    note="",
)

ATONEMENT = Weapon(
    name="Клинок искупления",
    base_atk=565.0,
    refinement=5,
    stats={S.ATK_PCT: 0.276},
    stats_by_refinement={
        5: {
            S.ATK_PCT: 0.32,
            S.BASE_EM: 128
        },
    },
    note="",
)

TEASPOON = Weapon(
    name="Чайная ложка",
    base_atk=674.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.44},
    stats_by_refinement={
        1: {
            S.ATK_PCT: 0.28,
            S.SC_BONUS: 0.16*3
        },
        2: {
            S.ATK_PCT: 0.35,
            S.SC_BONUS: 0.2*3
        },
        3: {
            S.ATK_PCT: 0.42,
            S.SC_BONUS: 0.24*3
        },
        4: {
            S.ATK_PCT: 0.49,
            S.SC_BONUS: 0.28*3
        },
        5: {
            S.ATK_PCT: 0.56,
            S.SC_BONUS: 0.32*3
        },
    },
    note="",
)

THOUSAND_SUNS = Weapon(
    name="Тысяча солнц",
    base_atk=741.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.11*2},
    stats_by_refinement={
        1: {
            S.CRIT_VALUE: 0.2,
            S.ATK_PCT: 0.28
        },
    },
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
                        f"урона звёздных реакций отряду"),
            temp(S.SC_BONUS, BREEZEBORNE_BONUS[r], BREEZEBORNE, target=TEAM,
                 source=f"Напевы ветра R{r}: +{BREEZEBORNE_BONUS[r]:.0%} "
                        f"урона звёздных реакций отряду"),)
        for r in BREEZEBORNE_BONUS
    },
)

ELEGY_BONUS_ATK = {r: 0.2 + 0.05 * (r - 1) for r in range(1, 6)}
ELEGY_BONUS_EM = {r: 100 + 20 * (r - 1) for r in range(1, 6)}

ELEGY_BOW = Weapon(
    name="Элегия",
    base_atk=608.0,
    refinement=1,
    buffs_by_refinement={
        r: (temp(S.ATK_PCT, ELEGY_BONUS_ATK[r], ELEGY, target=TEAM,
                 source=f"Элегия R{r}: +{ELEGY_BONUS_ATK[r]:.0%} "
                        f""),
            temp(S.BASE_EM, ELEGY_BONUS_EM[r], ELEGY, target=TEAM,
                 source=f"Элегия R{r}: +{ELEGY_BONUS_EM[r]:.0%} "
                        f""),)
        for r in ELEGY_BONUS_ATK
    },
)

#: Пассивка Смертельного боя (одна цель рядом): +24% АТК на R1, +6% за ранг.
DEATHMATCH_ATK = {r: 0.24 + 0.06 * (r - 1) for r in range(1, 6)}

DEATHMATCH = Weapon(
    name="Смертельный бой",
    base_atk=454.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.368 * 2},
    stats_by_refinement={r: {S.ATK_PCT: DEATHMATCH_ATK[r]} for r in DEATHMATCH_ATK},
    note="Копьё из боевого пропуска. Пассивка — вариант «меньше 2 врагов рядом».",
)

SCARLET_SANDS_BONUS = {r: 0.52 + 0.13 * (r - 1) + 3 * (0.28 + 0.07 * (r - 1))
                       for r in range(1, 6)}

SCARLET_SANDS = Weapon(
    name="Посох алых песков",
    base_atk=542.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.441 * 2},
    buffs_by_refinement={
        r: (Buff(S.FLAT_ATK,
                 lambda ctx, k=SCARLET_SANDS_BONUS[r]: k * ctx.own("em"),
                 target=SELF,
                 source=f"Посох алых песков R{r}: +{SCARLET_SANDS_BONUS[r]:.0%} МС в атаку"),)
        for r in SCARLET_SANDS_BONUS
    },
    note="Стаки Dream of the Scarlet Sands считаются полными (3).",
)


ECHOES = Weapon(
    name="Отголоски сердца",
    base_atk=565.0,
    refinement=5,
    stats={S.ATK_PCT: 0.276},
    stats_by_refinement={5:{S.BASE_EM:120,S.SC_BONUS:0.32}},
    note="",
)

KAGURA = Weapon(
    name="Истина кагура",
    base_atk=608.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.662},
    stats_by_refinement={1:{"dmg_bonus.skill":0.72,S.SC_BONUS:0.36},
        2:{"dmg_bonus.skill":0.90,S.SC_BONUS:0.45},
        3:{"dmg_bonus.skill":0.18*6,S.SC_BONUS:0.18*3},
        4:{"dmg_bonus.skill":0.21*6,S.SC_BONUS:0.21*3},
        5:{"dmg_bonus.skill":0.24*6,S.SC_BONUS:0.24*3},
        },
    
    note="",
)

# --------------------------------------------------------------------------- #
#  Оружие отрядов лунной кристаллизации (значения R5)                          #
# --------------------------------------------------------------------------- #
FLUTE_OF_EZPITZAL = Weapon(
    name="Флейта",
    base_atk=454.0,
    refinement=5,
    stats={S.DEF_PCT: 0.69},
    stats_by_refinement={5: {S.DEF_PCT: 0.32}},

    note="Одноручный меч. Пассивка R5: +32% ЗЩ.",
)

COVENANT_FROST_SNOW = Weapon(
    name="Завет мороза",
    base_atk=510.0,
    refinement=5,
    stats={S.DEF_PCT: 0.517},
    stats_by_refinement={5: {S.BASE_EM: 200.0}},
    note="Лук. Пассивка R5: +200 МС.",
)

salutation_returned_bonus = {r: 0.4 + 0.1*(r-1) for r in range(1,6)}

GOLDEN_OATH = Weapon(
    name="Золотая клятва",
    base_atk=542.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.882},
    stats_by_refinement={1: {S.DEF_PCT: 0.16},
                         2: {S.DEF_PCT: 0.16*1.25},
                        3: {S.DEF_PCT: 0.16*1.5},
                        4: {S.DEF_PCT: 0.16*1.75},
                        5: {S.DEF_PCT: 0.16*2},},
    buffs_by_refinement={r: (Buff("dmg_bonus.geo",salutation_returned_bonus[r],target=SELF),
                             Buff("lunar_bonus.lunar_crystallize",salutation_returned_bonus[r],target=SELF),
                             Buff("dmg_bonus.geo",salutation_returned_bonus[r]/2,target=OTHERS),
                             Buff("lunar_bonus.lunar_crystallize",salutation_returned_bonus[r]/2,target=OTHERS),)
                         for r in salutation_returned_bonus},
    note="",
)

DRAGONS_BANE = Weapon(
    name="Погибель драконов",
    base_atk=454.0,
    refinement=5,
    stats={S.BASE_EM: 221.0},
    stats_by_refinement={5: {S.DMG_BONUS: 0.36}},
    note="Копьё. Пассивка R5: +36% урона.",
)

PROTOTYPE_AMBER = Weapon(
    name="Янтарь",
    base_atk=510.0,
    refinement=5,
    stats={S.HP_PCT: 0.413},
    note="Катализатор. Пассивка не учитывается.",
)

nocturne_bonus = {r: 0.4 + 0.1*(r-1) for r in range(1,6)}

NOCTURNE = Weapon(
    name="Ноктюрн",
    base_atk=542.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.882},
    # крит-вэлью ко ВСЕМ лунным реакциям (ключ "crit_value.lunar")
    stats_by_refinement={1: {S.HP_PCT: 0.24,
                             "crit_value.lunar":0.6},
                         2: {S.HP_PCT: 0.28,
                              "crit_value.lunar":0.8},
                        3: {S.HP_PCT: 0.32,
                             "crit_value.lunar":1},
                        4: {S.HP_PCT: 0.36,
                             "crit_value.lunar":1.2},
                        5: {S.HP_PCT: 0.4,
                             "crit_value.lunar":1.4},},
    note="",
)

MOONSHARD = Weapon(
    name="Осколок луны",
    base_atk=542.0,
    refinement=1,
    stats={S.CRIT_VALUE: 0.882},
    stats_by_refinement={1: {S.DEF_PCT: 0.2,
                             "lunar_bonus.lunar_crystallize":0.64},
                         2: {S.DEF_PCT: 0.25,
                              "lunar_bonus.lunar_crystallize":0.8},
                        3: {S.DEF_PCT: 0.3,
                             "lunar_bonus.lunar_crystallize":0.96},
                        4: {S.DEF_PCT: 0.35,
                             "lunar_bonus.lunar_crystallize":1.12},
                        5: {S.DEF_PCT: 0.4,
                             "lunar_bonus.lunar_crystallize":1.28},},
    note="",
)

# --------------------------------------------------------------------------- #
#  Оружие отрядов лунных бутонов                                               #
# --------------------------------------------------------------------------- #
BLACKMARROW = Weapon(
    name="Blackmarrow",
    base_atk=454.0,
    refinement=5,
    stats={S.BASE_EM: 221.0},
    # +24% урона лунных бутонов и ещё +24% при Moonsign: Ascendant Gleam
    # (бонус к урону цветения пока не используется — реакции нет)
    stats_by_refinement={5: {"lunar_bonus.lunar_bloom": 0.24 + 0.24}},
    note="Катализатор. Значения пассивки — как в описании.",
)

#: Пассивка Реликвии истины по рангу: КШ, МС (Secret of Lies), КУ (Moon of Truth)
RELIQUARY_PASSIVE = {r: (0.08 + 0.02 * (r - 1), 80.0 + 20.0 * (r - 1), 0.24 + 0.06 * (r - 1))
                     for r in range(1, 6)}
#: Оба эффекта активны одновременно → МС и КУ ×1.5
RELIQUARY_BOTH = 1.5

#: Реликвия истины, когда выполнены ВСЕ условия (навык + урон лунных бутонов):
#: КШ, МС ×1.5 и КУ ×1.5. Для персонажей без лунных бутонов — RELIQUARY_OF_TRUTH.
RELIQUARY_OF_TRUTH_LUNAR = Weapon(
    name="Reliquary of Truth",
    base_atk=542.0,
    stats={S.CRIT_VALUE: 0.882},
    refinement=1,
    stats_by_refinement={
        r: {S.CRIT_VALUE: 2 * cr + cd * RELIQUARY_BOTH, S.BASE_EM: em * RELIQUARY_BOTH}
        for r, (cr, em, cd) in RELIQUARY_PASSIVE.items()
    },
    note="Сигна Нефер; Secret of Lies + Moon of Truth одновременно.",
)

NIGHTWEAVER_PASSIVE = {r: ((60 + 15 * (r - 1))*2)
                     for r in range(1, 6)}

Millennial_Hymn_bonus = {r: 0.4 + 0.1*(r-1) for r in range(1,6)}

NIGHTWEAVER_LUNAR = Weapon(
    name="Nightweaver",
    base_atk=542.0,
    stats={S.BASE_EM: 0.265},
    refinement=1,
    stats_by_refinement={
        r: {S.BASE_EM: NIGHTWEAVER_PASSIVE[r]}
        for r in NIGHTWEAVER_PASSIVE
    },
    buffs_by_refinement = {r:(Buff("lunar_bonus.lunar_bloom",Millennial_Hymn_bonus[r],target=TEAM),)
                           for r in Millennial_Hymn_bonus},
    note="Сигна Лаумы",
)

SPINDLELUTE = Weapon(
    name="Spindlelute",
    base_atk=510.0,
    refinement=5,
    stats_by_refinement={5: {S.BASE_EM: 200.0}},
    note="Катализатор. Пассивка R5: +200 МС.",
)

ALL = {w.name: w for w in (WANDERER_SONG, SUNNY_MORNING_SLEEP_IN, EXAIPHANES,
                           SILVER_LIGHT, SACFRAG,FAV_BOW)}

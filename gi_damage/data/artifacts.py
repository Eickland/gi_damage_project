"""
Наборы артефактов.

ВАЖНО: главные и побочные статы конкретных предметов сюда НЕ вносятся —
они задаются в сборке (Build.extra_stats). Здесь только эффекты наборов.
"""

from __future__ import annotations

from ..core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ..core.entities import ArtifactSet
from ..core.stats import S
from .tags import *

# --------------------------------------------------------------------------- #
INSTRUCTOR = ArtifactSet(
    name="Инструктор",
    pieces=4,
    stats_by_pieces={
        # 2 предмета: +80 МС носителю набора
        2: {S.BASE_EM: 80.0},
    },
    buffs_by_pieces={
        # 4 предмета: после срабатывания реакции +120 МС ВСЕМ членам отряда
        # (включая носителя) на 8 с. Условие срабатывания не моделируется —
        # считаем, что окно INST открыто.
        4: (
            Buff(S.BASE_EM, 120.0, target=TEAM, requires=(INST,), temporary=True,
                 source="Инструктор 4ч: +120 МС всему отряду"),
        ),
    },
    note="",
)

VIRIDESCENT = ArtifactSet(
    name="Изумрудная тень",
    pieces=4,
    buffs_by_pieces={
        4: (
            Buff("res_reduction.cryo", 0.40, target=TEAM, requires=(VV_CRYO,), temporary=True,
                 source="Изумрудная тень 4ч: -40% сопр. к стихии рассеивания"),
            Buff("res_reduction.pyro", 0.40, target=TEAM, requires=(VV_PYRO,), temporary=True,
                 source="Изумрудная тень 4ч: -40% сопр. к стихии рассеивания"),
            Buff("res_reduction.hydro", 0.40, target=TEAM, requires=(VV_HYDRO,), temporary=True,
                 source="Изумрудная тень 4ч: -40% сопр. к стихии рассеивания"),
            Buff("res_reduction.electro", 0.40, target=TEAM, requires=(VV_ELECTRO,), temporary=True,
                 source="Изумрудная тень 4ч: -40% сопр. к стихии рассеивания"),
            Buff(S.SSW_BONUS, 0.20, target=SELF, requires=(ON,),
             source="+20% урона звёздного рассеивания"),
        ),
    },
    note=("2ч: +15% анемо урона; 4ч: +60% урона рассеивания, +20% к урону звездного рассеивания и -40% сопр. цели "
          "к стихии рассеивания."),
)

MILLELITH = ArtifactSet(
    name="Милеллит",
    pieces=4,
    stats_by_pieces={2:{S.HP_PCT: 0.2}},
    buffs_by_pieces={
        4: (Buff(S.ATK_PCT, 0.2, target=TEAM,
                 source="Милеллит 4ч: +20% атаки всему отряду"),
            )
        },
    note="",
)

NOBLESSE = ArtifactSet(
    name="Знать",
    pieces=4,
    buffs_by_pieces={
        4: (Buff(S.ATK_PCT, 0.2, target=TEAM, requires=(NOBLE,), temporary=True,
                 source="Знать 4ч: +20% атаки всему отряду"),
            )
        },
    note="",
)

HEART_OF_FORGE = ArtifactSet(
    name="Сердце горна",
    pieces=4,
    stats_by_pieces={
        # 2 предмета: +18% атаки носителю
        2: {S.ATK_PCT: 0.18},
    },
    buffs_by_pieces={
        4: (Buff(S.SSW_BONUS, 0.50, target=TEAM,
         source="Сердце горна 4ч:+50% урона звёздного команде"),
            Buff(S.SC_BONUS, 0.50, target=TEAM,
         source="Сердце горна 4ч:+50% урона звёздного команде"),
            Buff(S.ATK_PCT, 0.12, target=SELF,
         source="Сердце горна 4ч:+12% атаки носителю"))
        },
    note="",
)

SCARLET_PROOF = ArtifactSet(
    name="Багряное доказательство",
    pieces=4,
    stats_by_pieces={
        # 2 предмета: +18% атаки носителю
        2: {S.ATK_PCT: 0.18},
    },
    buffs_by_pieces={
        4: (Buff(S.SSW_BONUS, 0.40, target=SELF,
         source="Багряное доказательство 4ч:+40% урона звёздного рассеивания"),
            Buff(S.CRIT_VALUE, 0.32, target=SELF,
         source="Багряное доказательство 4ч:+16% крит шанса носителю"))
        },
    note="",
)

DISENCHANTMENT = ArtifactSet(
    name="Разочарование",
    pieces=4,
    stats_by_pieces={
        # 2 предмета: +18% атаки носителю
        2: {S.ATK_PCT: 0.18},
    },
    buffs_by_pieces={
        4: (Buff(S.SC_BONUS, 0.40, target=SELF,
         source="Разочарование 4ч:+40% урона звёздного проводника"),
            Buff(S.CRIT_VALUE, 0.32, target=SELF,
         source="Разочарование 4ч:+16% крит шанса носителю"))
        },
    note="",
)

VOURUKASHA = ArtifactSet(
    name = "Сияние Вурукаши",
    pieces=2,
    stats_by_pieces={
        2: {S.HP_PCT: 0.2},
    },    
)

AUBADE = ArtifactSet(
    name = "Рассветная песнь",
    pieces=4,
    stats_by_pieces={
        2: {S.BASE_EM: 80},
    },
    buffs_by_pieces={
        4: (Buff(S.LUNAR_BONUS, 0.60, target=SELF, requires=(OFF,),
                 source="Рассветная песнь 4ч: +60% урона лунных реакций вне поля"),),
    },
)

NIGHT_SKY = ArtifactSet(
    name = "Ночь неба",
    pieces=4,
    stats_by_pieces={
        2: {S.BASE_EM: 80},
    },
    buffs_by_pieces={
        4: (Buff(S.CRIT_VALUE, 0.30 * 2, target=SELF,
                 source="Ночь неба 4ч: +30% крит. шанса"),
            Buff(S.LUNAR_BONUS, 0.10, target=TEAM,
                 source="Ночь неба 4ч: +10% урона лунных реакций отряду"),),
    },
)

SERENADE = ArtifactSet(
    name = "Серенада",
    pieces=4,
    buffs_by_pieces={
        4: (Buff(S.BASE_EM, 120.0, target=TEAM,
                 source="Серенада 4ч: +120 МС отряду"),
            Buff(S.LUNAR_BONUS, 0.10, target=TEAM,
                 source="Серенада 4ч: +10% урона лунных реакций отряду"),),
    },
)

DEEPWOOD = ArtifactSet(
    name = "Воспоминания леса",
    pieces=4,
    stats_by_pieces={
        2: {"dmg_bonus.dendro": 0.15},
    },
    buffs_by_pieces={
        4: (Buff("res_reduction.dendro", 0.30, target=TEAM,
                 source="Воспоминания леса 4ч: −30% дендро сопротивления"),),
    },
)

GILDED = ArtifactSet(
    name="Позолоченные сны",
    pieces=4,
    stats_by_pieces={2: {S.BASE_EM: 80}},
    buffs_by_pieces={
        4: (
            Buff(S.ATK_PCT, lambda ctx: 0.14 * ctx.count_allies(same_element=True),
                 target=SELF,
                 source="Позолоченные сны 4ч: +14% АТК за союзника той же стихии (до 3)"),
            Buff(S.BASE_EM, lambda ctx: 50.0 * ctx.count_allies(same_element=False),
                 target=SELF,
                 source="Позолоченные сны 4ч: +50 МС за союзника иной стихии (до 3)"),
        ),
    },
)

ALL = {a.name: a for a in (INSTRUCTOR, VIRIDESCENT, MILLELITH, HEART_OF_FORGE)}

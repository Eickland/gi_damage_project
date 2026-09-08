"""
Наборы артефактов.

ВАЖНО: главные и побочные статы конкретных предметов сюда НЕ вносятся —
они задаются в сборке (Build.extra_stats). Здесь только эффекты наборов.
"""

from __future__ import annotations

from ..core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ..core.entities import ArtifactSet
from ..core.stats import S
from .tags import INST, OFF, ON

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
    note="Носитель в пресете — Сахароза.",
)

VIRIDESCENT = ArtifactSet(
    name="Изумрудная тень",
    pieces=4,
    buffs_by_pieces={
        4: (
            # 4ч: -40% сопротивления цели к стихии, которую рассеяли.
            # В этом отряде рассеивается крио.
            # Работает, только если цель задана через Enemy.res (базовое
            # сопротивление); при Enemy.res_mult (готовые множители таблицы)
            # снижение уже учтено в самих множителях и повторно не применяется.
            Buff("res_reduction.cryo", 0.40, target=TEAM,
                 source="Изумрудная тень 4ч: -40% сопр. к стихии рассеивания"),
            Buff(S.SSW_BONUS, 0.20, target=SELF, requires=(ON,),
             source="+20% урона звёздного рассеивания"),
        ),
    },
    note=("2ч: +15% анемо урона; 4ч: +60% урона рассеивания, +20% к урону звездного рассеивания и -40% сопр. цели "
          "к стихии рассеивания. Бонус урона рассеивания в таблице «зашит» "
          "в постоянные слагаемые скобки EMM."),
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

EM_2_2_SET = ArtifactSet(
    name = "2+2 на МС",
    pieces=4,
    stats_by_pieces={
        2: {S.BASE_EM: 80},
        4: {S.BASE_EM: 80},
    },    
)

ATK_2_2_SET = ArtifactSet(
    name = "2+2 на атк",
    pieces=4,
    stats_by_pieces={
        2: {S.ATK_PCT: 0.18},
        4: {S.ATK_PCT: 0.18},
    },    
)

ALL = {a.name: a for a in (INSTRUCTOR, VIRIDESCENT, MILLELITH, HEART_OF_FORGE)}

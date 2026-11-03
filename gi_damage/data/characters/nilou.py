"""
Нилу — гидро, меч. Саппорт (не из лунного региона — не Moonsign).
Масштабируется от макс. HP.

Ротация: E E E (Кружащие шаги), 2.5 с — все удары на поле:
    E                 — Танец Хафткаршвар:     6.01% HP (гидро, урон навыка)
    Кружащие шаги, 1  —                         5.87% HP
    Кружащие шаги, 2  —                         7.13% HP
    Водяное колесо    — 3-й шаг танца:          9.11% HP
Урон в состоянии Кружащих шагов — гидро урон навыка, другими инфузиями
не отменяется.

База: HP 15 185, +28.8% HP (бонус возвышения).

C2  Дождь лепестков звёздного неба: −35% гидро и −35% дендро сопротивления
    (условия срабатывания не моделируются — считается всегда).
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ
from ..tags import *

NILOU_NAME = "Нилу"

# --------------------------------------------------------------------------- #
#  Множители (доли макс. HP)                                                   #
# --------------------------------------------------------------------------- #
SKILL_MV = 0.0601            # Танец Хафткаршвар
WHIRLING_1_MV = 0.0587       # Кружащие шаги, 1-й удар
WHIRLING_2_MV = 0.0713       # Кружащие шаги, 2-й удар
WATER_WHEEL_MV = 0.0911      # Водяное колесо (3-й шаг)

C2_RES_SHRED = 0.35

NILOU_TIME = 3.5


NILOU_KIT = Character(
    name=NILOU_NAME,
    element="hydro",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_HP: 15185.0,
        S.HP_PCT: 0.288,
        S.BASE_ATK: 230.0,
        S.CRIT_VALUE: 0.6,       # 5% КШ / 50% КУ
    },
    buffs=(),
    sources=(),
    constellations={
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff("res_reduction.hydro", C2_RES_SHRED, target=TEAM,
                     source="C2 Нилу: −35% гидро сопротивления"),
                Buff("res_reduction.dendro", C2_RES_SHRED, target=TEAM,
                     source="C2 Нилу: −35% дендро сопротивления"),
            ),
        ),
    },
    note="Гидро саппорт (не Moonsign).",
)

NILOU_COMBO_DICT = {
    # E + Кружащие шаги (E E): все удары — урон навыка, на поле
    "eee": with_rotation(
        NILOU_KIT,
        sources=(
            elemental("Танец Хафткаршвар", "hp", SKILL_MV, "hydro", "skill", [occ(1, ON)]),
            elemental("Кружащие шаги, 1-й удар", "hp", WHIRLING_1_MV, "hydro", "skill",
                      [occ(1, ON)]),
            elemental("Кружащие шаги, 2-й удар", "hp", WHIRLING_2_MV, "hydro", "skill",
                      [occ(1, ON)]),
            elemental("Водяное колесо", "hp", WATER_WHEEL_MV, "hydro", "skill", [occ(1, ON)]),
        ),
    ),
}

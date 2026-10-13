"""
Диона
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_swirl

DIONA_KIT = Character(
    name="Диона",
    element="cryo",
    weapon_type="bow",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 212.0,
        S.CRIT_VALUE: 0.6,
        "dmg_bonus.cryo":0.24,
    },
    buffs = (temp(S.BASE_EM, 200, requires=(ON,CATS_TAIL), target=TEAM,
                     source="С6 Диона, +200 МС активному персонажу"),
             temp(S.SSW_BONUS, 0.4, requires=(ON,CATS_TAIL), target=TEAM,
                    source="С6 Диона, +40% урона к звездным реакциям активному")),
    sources=(),
    note="",
)

DIONA_COMBO_DICT = {
    "off_field" : with_rotation(
        DIONA_KIT, sources=(
        elemental("Использование навыка", "atk", 0.7546, "cryo", "skill",
                  [occ(5, ON,),]),
        elemental("Icy Paws", "atk", 0.7546, "cryo", "skill",
                  [occ(2, OFF,), occ(3, OFF, DREAM)]),
        elemental("Использование взрыва стихии", "atk", 1.44, "cryo", "burst",
                  [occ(1, ON,),]),
        elemental("Drunken Mist", "atk", 0.9475, "cryo", "burst",
                  [occ(6, OFF,),]),               
        ))
}
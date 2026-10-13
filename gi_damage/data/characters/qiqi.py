"""
Ци Ци
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_swirl

QIQI_KIT = Character(
    name="Ци Ци",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 287.0,
        S.CRIT_VALUE: 0.6,
    },
    buffs = (temp(S.SSW_BONUS, 0.5, requires=(SEVEN_SACRED,), target=TEAM,
                    source="Ци ци, +50% урона к звездным реакциям команде"),),
    sources=(),
    note="",
)

QIQI_COMBO_DICT = {
    "off_field" : with_rotation(
        QIQI_KIT, sources=(
        elemental("Использование навыка", "atk", 1.728, "cryo", "skill",
                  [occ(1, ON,),]),
        elemental("Herald of Frost", "atk", 0.648, "cryo", "skill",
                  [occ(4, OFF,), occ(6, OFF, DREAM)]),             
        ))
}
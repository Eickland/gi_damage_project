"""
Фарузан
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW
from ...core.sources import elemental, occ, stellar_swirl

FARUZAN_KIT = Character(
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

FARUZAN_COMBO_DICT = {
    "ssw_combo" : with_rotation(
        FARUZAN_KIT, sources=(
        elemental("Использование навыка", "atk", 2.6784, "anemo", "skill",
                  [occ(1, ON,),]),
        elemental("Обвал под давлением", "atk", 1.944, "anemo", "skill",
                  [occ(2, OFF,), occ(4, OFF, DREAM)]),
        elemental("Использование взрыва стихии", "atk", 6.7968, "anemo", "burst",
                  [occ(1, ON,),]),             
        ))
}
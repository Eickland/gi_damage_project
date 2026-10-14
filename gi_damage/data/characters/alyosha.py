"""
Алеша
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW
from ...core.sources import elemental, occ, stellar_swirl

ALYOSHA_KIT = Character(
    name="Алеша",
    element="electro",
    weapon_type="polearm",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 265.0,
        S.CRIT_VALUE: 0.6,
    },
    buffs = (Buff(S.ATK_PCT, 0.212, target=TEAM,requires=(ON,),
                     source="Hunter's Precision ATK Bonus"),
            Buff(S.SC_BONUS, 0.2, target=TEAM,requires=(ON,),
                     source="Into the Fray"),),
    sources=(),
    constellations = {
        3: Constellation(
            number=3,
            name="C3",
            buffs=(
                Buff(S.ATK_PCT, 0.038, target=TEAM, requires=(ON,),
                     source="Hunter's Precision ATK Bonus C3"),
            ),
        ),
        4: Constellation(number=5, name="C5"),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff(S.BASE_EM, 100.0, target=TEAM, requires=(ON,),
                     source="Standard Reclaimed"),
                Buff(S.ATK_PCT, 0.25, target=TEAM,requires=(ON,),
                        source="Hunter's Precision ATK Bonus C6"),
                Buff(S.SC_BONUS, 0.2, target=TEAM,requires=(ON,),
                        source="Into the Fray C6"),
            ),
        ),        
    },
    note="",
)

ALYOSHA_COMBO_DICT = {
    "sc_combo" : with_rotation(
        ALYOSHA_KIT, sources=(
        elemental("Thunderbolt Strike", "atk", 5.161, "electro", "skill",
                  [occ(1, ON,),]),
        elemental("Fulgurite Hunting Field DMG", "atk", 1.3493, "electro", "burst",
                  [occ(2, OFF,)]),
        elemental("Tugarin DMG", "atk", 0.904, "electro", "burst",
                  [occ(10, OFF,),]),             
        ))
}
"""
Сахароза
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW
from ...core.sources import elemental, occ, stellar_swirl

SUCROSE_KIT = Character(
    name="Сахароза",
    element="anemo",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 170.0,
        S.CRIT_VALUE: 0.6,
        "dmg_bonus.anemo": 0.24,
    },
    buffs=(
        temp(S.FLAT_EM,
             lambda ctx: 0.20 * ctx.stat("Сахароза", "em", ctx.mirror(ON, keep=[INST])),
             INST, target=OTHERS,
             source="Сахароза A4: +20% своего МС отряду"),
        temp(S.BASE_EM, 50.0, INST, target=OTHERS,
             source="+50 МС в окне Инструктора при активации элементальной реакции"),
    ),
    sources=(),
    note="",
)

SUCROSE_COMBO_DICT = {
    "no_burst_combo" : with_rotation(
        SUCROSE_KIT, sources=(
        elemental("Использование навыка (АТК)", "atk", 3.8016, "anemo", "skill",
                  [occ(2, ON,)]),            
        )
    ),
    "cryo_burst_combo" : with_rotation(
        SUCROSE_KIT, sources=(
        elemental("Использование навыка (АТК)", "atk", 3.8016, "anemo", "skill",
                  [occ(2, ON,)]),            
        elemental("Основной переодический урон", "atk", 2.664, "anemo", "burst", [occ(3, OFF, INST)]),
        
        elemental("Дополнительный переодический урон", "atk", 0.792, "cryo", "burst", [occ(3, OFF, INST)]),)

    ),    
}
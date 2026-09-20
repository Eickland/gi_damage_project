"""
Весна

"""

from __future__ import annotations
from dataclasses import replace

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.sources import Occurrence, elemental, occ, stellar_swirl
from ...core.stats import S
from ..tags import (DREAM, INST, OFF, ON, FROSTGLOW, BREEZEBORNE,
                    ARMED, DA1, DA2, DA3, DA4, DA5, DA6)

# =========================================================================== #
#  Весна — анемо, main dps (меч)
# =========================================================================== #

DA_STACK = "vesna_da_stacks"

VESNA_KIT = Character(
    name="Весна",
    element="anemo",
    weapon_type="sword",
    default_field=ON,
    crit_mode="balance",

    stats={
        S.BASE_ATK: 354.0,
        S.CRIT_VALUE: 0.6+0.384,
        S.ATK_PCT: 0.24
    },
    buffs = (Buff(S.SSW_BASE_INC, 0.14, target=TEAM, source="A3 Весна"),
        *(Buff(DA_STACK, n, target=SELF, requires=(tag,),
               source=f"Disciplinary Action: da={n}")
          for n, tag in enumerate((DA1, DA2, DA3, DA4, DA5, DA6), start=1)),),
    multipliers={
        "disciplinary_action": lambda stats: 1.0 + 0.10 * stats.get(DA_STACK, 0.0),
    },
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff(S.SSW_BONUS, 0.2,
                     target=SELF, requires=(ON,),
                     source="C1"),
            ),

        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.ATK_PCT, 0.4,
                     target=SELF, requires=(ON,),
                     source="C2"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Windborne Sword Lv2 — Spirit Blade": lambda s: replace(s, mv=2.38),
                "Windborne Sword Lv3 — Spirit Blade x4": lambda s: replace(s, mv=0.952),
                "Windborne Sword Lv3 — Spirit Blade x4, C1": lambda s: replace(s, mv=0.952),
                "Windborne Sword Lv3 Spirit Blade Final Hit": lambda s: replace(s, mv=3.32),
                "Windborne Sword Lv3 Spirit Blade Final Hit, C1": lambda s: replace(s, mv=3.32),
            },
        ),
        4: Constellation(
            number=4,
            name="C4",
            buffs=(
                Buff(S.ATK_PCT, 0.48,
                     target=SELF, requires=(ON,),
                     source="C4"),
            ),
        ),
        5: Constellation(
            number=5,
            name="C5",
            patches={
                "Взрыв — Клинок Духа": lambda s: replace(s, mv=5.593),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("elevation.stellar_swirl", 0.2, target=SELF,
                    source="C6: +20% возвышения урона SSW самой Весны"),
            ),
        ),
    },
    note="Анемо, меч, main dps..",
)

VESNA_COMBO_DICT = {
    "ssw_burst_combo" : with_rotation(VESNA_KIT,sources=(
        elemental("Обычный удар, N1", "atk", 0.799, "anemo", "normal",
                  [occ(4, ON)]),
        elemental("Заряженная атака", "atk", 2.6299, "anemo", "charged",
                  [occ(4, ON)]),
        
        elemental("Использование навыка", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON)]),

        elemental("Windborne Sword Lv1", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON, ARMED)],
                  extra_tags=("windborne_sword",)),

        elemental("Windborne Sword Lv2", "atk", 1.08, "anemo", "skill",
                  [occ(1, ON, ARMED)],
                  extra_tags=("windborne_sword",)),

        stellar_swirl("Windborne Sword Lv2 — Spirit Blade", "atk", 2.016,
                  "anemo",[occ(1, ON, ARMED, DA1, BREEZEBORNE, FROSTGLOW)],"skill",
                  extra_tags=("spirit_blade",),
                  multipliers=("disciplinary_action",)),

        stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4", "atk", 0.8064,
                  "anemo",
                  [occ(4, ON, ARMED, DA3, BREEZEBORNE, FROSTGLOW), occ(4, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW), occ(4, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW)], "skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
        stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit", "atk",
                  2.8224, "anemo", 
                  [occ(1, ON, ARMED, DA3, BREEZEBORNE, FROSTGLOW), occ(1, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW), occ(1, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW)],"skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),

        elemental("Перо ветра", "atk", 0.1872, "anemo", "skill",
                  [occ(5, ON, ARMED)]),

        stellar_swirl("Взрыв — Клинок Духа", "atk", 4.7376, "anemo",
                  [occ(1, ON, ARMED, DA2, BREEZEBORNE, FROSTGLOW)], "burst",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
    
    ), constellation_sources={
        1: (
            stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4, C1", "atk", 0.8064,
                        "anemo",
                        [occ(4, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)], "skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
            stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit, C1", "atk",
                        2.8224, "anemo", 
                        [occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)],"skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),                
            ),
        6: (elemental("C6: Windborne Sword: Transpose", "atk", 1.50,
                          "anemo", "skill", [occ(3, ON, ARMED, BREEZEBORNE, FROSTGLOW)],
                          extra_tags=("transpose",)),
            stellar_swirl("C6: Windborne Sword: Transpose — Клинок Духа",
                          "atk", 2.00, "anemo", 
                          [occ(3, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)],"skill",
                          extra_tags=("spirit_blade",
                                      "transpose"),multipliers=("disciplinary_action",)),
            ),      
        },
    constellation_patches={
        2: {"Windborne Sword Lv2 — Spirit Blade": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
                "Windborne Sword Lv3 — Spirit Blade x4": lambda s: replace(s, occurrences=[occ(12, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
                "Windborne Sword Lv3 Spirit Blade Final Hit": lambda s: replace(s, occurrences=[occ(3, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
                "Взрыв — Клинок Духа": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            },
        }),

    "ssw_no_burst_combo" : with_rotation(VESNA_KIT,sources=(
        elemental("Обычный удар, N1", "atk", 0.799, "anemo", "normal",
                  [occ(5, ON)]),
        elemental("Обычный удар, N2", "atk", 0.9622, "anemo", "normal",
                  [occ(1, ON)]),
        elemental("Обычный удар, N3", "atk", 0.5551, "anemo", "normal",
                  [occ(2, ON)]),
        elemental("Заряженная атака", "atk", 2.6299, "anemo", "charged",
                  [occ(5, ON)]),
        
        elemental("Использование навыка", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON)]),

        elemental("Windborne Sword Lv1", "atk", 0.72, "anemo", "skill",
                  [occ(1, ON, ARMED)],
                  extra_tags=("windborne_sword",)),

        elemental("Windborne Sword Lv2", "atk", 1.08, "anemo", "skill",
                  [occ(1, ON, ARMED)],
                  extra_tags=("windborne_sword",)),

        stellar_swirl("Windborne Sword Lv2 — Spirit Blade", "atk", 2.016,
                  "anemo",[occ(1, ON, ARMED, DA1, BREEZEBORNE, FROSTGLOW)],"skill",
                  extra_tags=("spirit_blade",),
                  multipliers=("disciplinary_action",)),

        stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4", "atk", 0.8064,
                  "anemo",
                  [occ(4, ON, ARMED, DA2, BREEZEBORNE, FROSTGLOW), occ(4, ON, ARMED, DA3, BREEZEBORNE, FROSTGLOW),
                   occ(4, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW)], "skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
        stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit", "atk",
                  2.8224, "anemo", 
                  [occ(1, ON, ARMED, DA2, BREEZEBORNE, FROSTGLOW), occ(1, ON, ARMED, DA3, BREEZEBORNE, FROSTGLOW),
                   occ(1, ON, ARMED, DA4, BREEZEBORNE, FROSTGLOW)],"skill",
                  extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),

        elemental("Перо ветра", "atk", 0.1872, "anemo", "skill",
                  [occ(5, ON, ARMED)]),

    
    ), constellation_sources={
        1: (stellar_swirl("Windborne Sword Lv3 — Spirit Blade x4, C1", "atk", 0.8064,
                        "anemo",
                        [occ(4, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW)], "skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),
            stellar_swirl("Windborne Sword Lv3 Spirit Blade Final Hit, C1", "atk",
                        2.8224, "anemo", 
                        [occ(1, ON, ARMED, DA5, BREEZEBORNE, FROSTGLOW)],"skill",
                        extra_tags=("spirit_blade",),multipliers=("disciplinary_action",)),                
            ),
        6: (elemental("C6: Windborne Sword: Transpose", "atk", 1.50,
                          "anemo", "skill", [occ(3, ON, ARMED, BREEZEBORNE, FROSTGLOW)],
                          extra_tags=("transpose",)),
            stellar_swirl("C6: Windborne Sword: Transpose — Клинок Духа",
                          "atk", 2.00, "anemo", 
                          [occ(3, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)],"skill",
                          extra_tags=("spirit_blade",
                                      "transpose"),multipliers=("disciplinary_action",)),
            ),      
        },
    constellation_patches={
        2: {"Windborne Sword Lv2 — Spirit Blade": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE,    FROSTGLOW)]),
            "Windborne Sword Lv3 — Spirit Blade x4": lambda s: replace(s, occurrences=[occ(12, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            "Windborne Sword Lv3 Spirit Blade Final Hit": lambda s: replace(s, occurrences=[occ(3, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            "Взрыв — Клинок Духа": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            "Windborne Sword Lv3 — Spirit Blade x4, C1": lambda s: replace(s, occurrences=[occ(4, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            "Windborne Sword Lv3 Spirit Blade Final Hit, C1": lambda s: replace(s, occurrences=[occ(1, ON, ARMED, DA6, BREEZEBORNE, FROSTGLOW)]),
            },
        })    

}
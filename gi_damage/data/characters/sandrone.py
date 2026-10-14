"""
Сандроне.


"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_swirl, stellar_conduct

SANDRONE_KIT = Character(
    name="Сандроне",
    element="cryo",
    weapon_type="claymore",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 342,
        S.CRIT_VALUE: 0.6 + 0.384,
    },
    buffs=(
        Buff(S.SSW_BASE_INC, 0.14, target=TEAM, source="A3 Сандроне"),
        Buff(S.SC_BASE_INC, 0.14, target=TEAM, source="A3 Сандроне"),
        Buff(S.BASE_EM, 160, target=SELF, source="A2 Сандроне"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff(S.SC_BONUS, 0.3, target=TEAM, requires=(DECODING,),
                     source="+30% бонуса к звездному урону, пока Сандроне на поле"),
                Buff(S.SSW_BONUS, 0.3, target=TEAM, requires=(DECODING,),
                     source="+30% бонуса к звездному урону, пока Сандроне на поле"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.CRIT_VALUE, 0.4, target=SELF, requires=(ON,),
                     source="Бонус к крит урону заряженных атак"),
                Buff(S.CRIT_VALUE, 0.2, target=SELF, requires=(ON,SANDRONE_CA_STACKS_1),
                     source="Бонус к крит урону заряженных атак"),
                Buff(S.CRIT_VALUE, 0.4, target=SELF, requires=(ON,SANDRONE_CA_STACKS_2),
                     source="Бонус к крит урону заряженных атак"),
                Buff(S.CRIT_VALUE, 0.6, target=SELF, requires=(ON,SANDRONE_CA_STACKS_3),
                     source="Бонус к крит урону заряженных атак"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Charged Attack Condensed Beam Stellar-Conduct": lambda s: replace(s, mv=(1.957)),
            },
        ),
        4: Constellation(number=4, name="C4"),
        5: Constellation(
            number=5,
            name="C5",
            patches={
                "Convective Inhibition Ray Stellar-Conduct DMG": lambda s: replace(s, mv=2*4.6863),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("elevation.stellar_swirl", 0.20, target=SELF,
                     source="C6: +20% возвышения урона SSW самой Сандроне"),
                Buff("elevation.stellar_conduct", 0.20, target=SELF,
                     source="C6: +20% возвышения урона SC самой Сандроне"),
            ),
        ),
    },
    note="",
)

SANDRONE_COMBO_DICT = {
    "sandrone_sc_sucrose_combo" : with_rotation(
    SANDRONE_KIT,
    sources=(
        elemental("Prism Shot DMG", "atk", 0.5832, "cryo", "skill",
                  [occ(3, ON,VV_CRYO,TTDS_FULL)]),
        elemental("Charged Attack Sweeping Fire DMG", "atk", 0.85, "cryo", "charged",
                  [occ(27, ON,VV_CRYO,TTDS_FULL), occ(9, ON,)]),
        elemental("Bombardment DMG", "atk", 1.5879, "cryo", "burst",
                  [occ(3, ON,VV_CRYO,TTDS_FULL),]),
        stellar_conduct("Charged Attack Condensed Beam Stellar-Conduct", "atk", 1.615,
                      "cryo", [occ(4, ON, INST,BREEZEBORNE,VV_CRYO,TTDS_FULL,SEVEN_SACRED,CATS_TAIL),
                               occ(3, ON, INST,BREEZEBORNE,VV_CRYO,SEVEN_SACRED,CATS_TAIL),
                               occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL),
                               occ(1, ON,),], kind="charged",polar_stacks=7),
        stellar_conduct("Prism Shot Stellar-Conduct DMG", "atk", 0.3888*4,
                      "cryo", [occ(1, ON, INST,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                               occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                               occ(1, ON,),], kind="skill",polar_stacks=7),
        stellar_conduct("Convective Inhibition Ray Stellar-Conduct DMG", "atk", 2*3.9696, "cryo",
                      [occ(1, ON, INST,BREEZEBORNE,FROSTGLOW,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED)], kind="burst",polar_stacks=8),
    ),
    constellation_patches={
        1: {
            "Charged Attack Condensed Beam Stellar-Conduct": lambda s: replace(s, occurrences=[
                occ(5, ON, INST,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL),
                occ(2, ON,BREEZEBORNE,VV_CRYO,INST),
                occ(4, ON,BREEZEBORNE,VV_CRYO,INST,CATS_TAIL,SEVEN_SACRED),
                ]),
            "Prism Shot Stellar-Conduct DMG": lambda s: replace(s, occurrences=[
                occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                occ(1, ON,BREEZEBORNE,VV_CRYO,SEVEN_SACRED),
                ]),            
        },
        2: {
            "Charged Attack Condensed Beam Stellar-Conduct": lambda s: replace(s, occurrences=[
                occ(5, ON, INST,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL),
                occ(2, ON,BREEZEBORNE,VV_CRYO,INST,SANDRONE_CA_STACKS_1),
                occ(2, ON,BREEZEBORNE,VV_CRYO,INST,CATS_TAIL,SEVEN_SACRED,SANDRONE_CA_STACKS_2),
                occ(2, ON,BREEZEBORNE,VV_CRYO,INST,CATS_TAIL,SEVEN_SACRED,SANDRONE_CA_STACKS_3),
                ]),
            "Prism Shot Stellar-Conduct DMG": lambda s: replace(s, occurrences=[
                occ(1, ON,BREEZEBORNE,VV_CRYO,TTDS_FULL,CATS_TAIL,SEVEN_SACRED),
                occ(1, ON,BREEZEBORNE,VV_CRYO,SEVEN_SACRED),
                ]),            
        },
    },
    constellation_sources={
        4: (
            stellar_conduct("Prismatic Resonance Cannon",
                          "atk", 1.25, "cryo",
                          [occ(1, ON,VV_CRYO,CATS_TAIL,SEVEN_SACRED), occ(2, ON, INST, BREEZEBORNE,TTDS_HALF,VV_CRYO,CATS_TAIL,SEVEN_SACRED)],polar_stacks=7),
        ),
        6: (
            stellar_conduct("Condensed Cluster Beam Stellar-Conduct",
                          "atk", 0.8, "cryo",
                          [occ(6, ON, INST, BREEZEBORNE,TTDS_HALF,VV_CRYO,CATS_TAIL,SEVEN_SACRED),
                           occ(2, ON, INST,VV_CRYO,CATS_TAIL,SEVEN_SACRED),
                           occ(2, ON, INST,VV_CRYO,SEVEN_SACRED),
                           ],polar_stacks=7),
        ),
    },
),

}
"""
Крио ГГ (Крио Путешественник) — часть кита, НЕ зависящая от ротации/отряда.

Источники урона (в т.ч. по созвездиям) сюда не входят — подставляются
per-team через core.entities.with_rotation(), см. data/teams/*.py.

Скилсет (множители — константы ниже):
    Обычная атака «Чужеземный холодный блеск»: N1–N5, заряженная атака
        (110.5% + 142.8%), высокий удар в падении 315.64%.
    Взрыв стихии «Морозное копьё»: Ледяное копьё — урон звёздного проводника
        66.16% за бросок (5 бросков) + Морозное сияние 3.31% за уровень
        (8 уровней). C4: 78.1% и 3.91%.
    «Вечно пронизывающий мороз» (звёздный проводник): во время Леденящей звезды
        обычные / заряженные атаки и атаки в падении — крио урон (инфузия не
        перебивается), к их множителю напрямую прибавляется +80% АТК.
    Специальная заряженная атака — та же, что в комбо рассеивания
        (110.5% + 140% и 142.8% + 140%); в версии проводника — урон звёздного
        проводника.

Комбо «ДД на поле через звёздный проводник» (cmc_sc_dd_combo), 8.7 с:
    N2 P N2 N2 C N2 Q N2 N2  — 6 × (N1 + N2), высокий удар, спец. заряженная
    атака, взрыв. Удары звёздного проводника (заряженная и взрыв) — 11 стаков.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_swirl, stellar_conduct

# --------------------------------------------------------------------------- #
#  Множители (в долях АТК)                                                     #
# --------------------------------------------------------------------------- #
NORMAL_MV = {1: 0.8789, 2: 0.8585, 3: 1.0472, 4: 1.1526, 5: 1.3991}
CHARGED_MV = (1.105, 1.428)              # обычная заряженная атака (2 удара)
HIGH_PLUNGE_MV = 3.1564

#: «Вечно пронизывающий мороз»: +80% АТК к множителю N / CA / атак в падении
EVERPIERCING_FROST_ATK = 0.80

#: Специальная заряженная атака: базовые множители CA + 140% (как в комбо SSW)
SPECIAL_CA_EXTRA = 1.40
SPECIAL_CA_MV = (CHARGED_MV[0] + SPECIAL_CA_EXTRA, CHARGED_MV[1] + SPECIAL_CA_EXTRA)

#: Взрыв «Морозное копьё», урон звёздного проводника: копьё + 8 уровней сияния
SPEAR_SC_MV, SPEAR_SC_MV_C4 = 0.6616, 0.781
FROSTGLOW_SC_PER_STACK, FROSTGLOW_SC_PER_STACK_C4 = 0.0331, 0.0391
FROSTGLOW_STACKS = 8
SPEAR_HITS = 5
BURST_SC_MV = SPEAR_SC_MV + FROSTGLOW_STACKS * FROSTGLOW_SC_PER_STACK
BURST_SC_MV_C4 = SPEAR_SC_MV_C4 + FROSTGLOW_STACKS * FROSTGLOW_SC_PER_STACK_C4

#: Стаки звёздного проводника (polar stacks) для ударов ДД-версии
CMC_SC_POLAR_STACKS = 11

CMC_SC_DD_TIME = 9.2

CRYO_MC_KIT = Character(
    name="Крио ГГ",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 212.0 + 7 + 3,
        S.BASE_EM: 160 + 15 + 60,
        S.CRIT_VALUE: 0.6 + 0.2 + 0.2,
        S.ATK_PCT: 0.2 + 0.24,
    },
    buffs=(
        Buff(S.SSW_BASE_INC, 0.07, target=TEAM, source="A3 Крио ГГ"),
    ),
    sources=(),
    constellations={
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.BASE_EM, 120.0, target=TEAM, requires=(ON,),
                     source="+120 МС активному персонажу"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Взрыв — SSW": lambda s: replace(s, mv=(1.1715 + 8 * 0.0586)),
                "Взрыв — SC": lambda s: replace(s, mv=BURST_SC_MV_C4),
            },
        ),
        5: Constellation(
            number=5,
            name="C5",
            patches={
                "Использование навыка (АТК)": lambda s: replace(s, mv=1.9482),
                "Навык (АТК)": lambda s: replace(s, mv=0.4546),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                temp(S.SSW_BONUS, 0.4, FROSTGLOW, target=OTHERS,
                     source="+40% к урону звездных реакций на 15с после применения взрыва стихий"),
                temp(S.SC_BONUS, 0.4, FROSTGLOW, target=OTHERS,
                     source="+40% к урону звездных реакций на 15с после применения взрыва стихий"),
            ),

        ),
    },
    note="",
)

CMC_COMBO_DICT = {
    "cmc_ssw_mizuki_combo" : with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON,VV_CRYO)]),
        elemental("Навык (АТК)", "atk", 0.3851, "cryo", "skill",
                  [occ(5, OFF, DREAM,VV_CRYO), occ(3, OFF,VV_CRYO)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST,BREEZEBORNE,VODYA_LEAD,VV_CRYO,SEVEN_SACRED,CATS_TAIL)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST,BREEZEBORNE,VODYA_LEAD,VV_CRYO,SEVEN_SACRED,CATS_TAIL)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST,BREEZEBORNE,VODYA_LEAD,VV_CRYO,SEVEN_SACRED,CATS_TAIL)], kind="burst"),
    ),
    constellation_patches={
        4: {
            "Навык (АТК)": lambda s: replace(s, occurrences=[occ(9, OFF, DREAM,VV_CRYO), occ(3, OFF,VV_CRYO)]),
        },
    },
),
    "cmc_ssw_vesna_combo" : with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON,VV_CRYO)]),
        elemental("Навык (АТК)", "atk", 0.3851, "cryo", "skill",
                  [occ(5, OFF,VV_CRYO), occ(3, OFF,VV_CRYO)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST,VV_CRYO)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST,VV_CRYO)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST,VV_CRYO)], kind="burst"),
    ),
    constellation_patches={
        4: {
            "Навык (АТК)": lambda s: replace(s, occurrences=[occ(9, OFF,VV_CRYO), occ(3, OFF,VV_CRYO)]),
        },
    },
),
    # ДД на поле через звёздный проводник: N2 P N2 N2 C N2 Q N2 N2, 8.7 с.
    # Окна отряда: все удары — под A4 Сахарозы (INST) и Изумрудной тенью (VV_CRYO).
    "cmc_sc_dd_combo": with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Обычная атака 1 (крио)", "atk", NORMAL_MV[1] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(6, ON, INST, VV_CRYO)]),
        elemental("Обычная атака 2 (крио)", "atk", NORMAL_MV[2] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(6, ON, INST, VV_CRYO)]),
        elemental("Высокий удар в падении (крио)", "atk", HIGH_PLUNGE_MV + EVERPIERCING_FROST_ATK,
                  "cryo", "plunge", [occ(1, ON, INST, VV_CRYO)]),
        stellar_conduct("Заряженная атака — SC, 1", "atk", SPECIAL_CA_MV[0], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF)], kind="charged",
                        polar_stacks=CMC_SC_POLAR_STACKS),
        stellar_conduct("Заряженная атака — SC, 2", "atk", SPECIAL_CA_MV[1], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF)], kind="charged",
                        polar_stacks=CMC_SC_POLAR_STACKS),
        stellar_conduct("Взрыв — SC", "atk", BURST_SC_MV, "cryo",
                        [occ(SPEAR_HITS, ON, INST, VV_CRYO, TTDS_HALF)], kind="burst",
                        polar_stacks=CMC_SC_POLAR_STACKS),
    ),
),
}

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

Комбо «ДД через звёздный проводник, с навыком» (cmc_sc_dd_e_combo), 6.4 с:
    E N2 N2 C Q N2  — навык (урон применения), 3 × (N1 + N2), спец. заряженная
    атака, взрыв. Стаки и окна — как в cmc_sc_dd_combo.

Комбо с заполнителем (cmc_sc_dd_combo_<k>n2, k = 1…CMC_FILLER_MAX):
    cmc_sc_dd_combo + k дополнительных N2 (N1 + N2) по CMC_N2_TIME = 0.6 с.
    Доп. удары получают те же окна баффов, что и остальные N1/N2 комбо.
    Нужны, чтобы ротация была не короче отката взрывов Анастасии и Даники
    (бета: 18 с) — вместо ручных добавок ко времени Крио ГГ.
"""

from __future__ import annotations
import math
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import Occurrence, elemental, occ, stellar_swirl, stellar_conduct

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
BURST_SC_MV = SPEAR_SC_MV + FROSTGLOW_STACKS * FROSTGLOW_SC_PER_STACK
BURST_SC_MV_C4 = SPEAR_SC_MV_C4 + FROSTGLOW_STACKS * FROSTGLOW_SC_PER_STACK_C4


CMC_SC_DD_TIME = 9.2
#: Комбо cmc_sc_dd_e_combo: E N2 N2 C Q N2
CMC_SC_DD_E_TIME = 6.4
#: Время одного дополнительного N2 (N1 + N2) — заполнитель ротации
CMC_N2_TIME = 0.6
CMC_FILLER_MAX = 6

CRYO_MC_KIT = Character(
    name="Крио ГГ",
    element="cryo",
    weapon_type="sword",
    default_field=OFF,
    polar_on_field=4.0,   # стаки Polestar отряду
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

#: Крио ГГ в ДД-стойке (на поле, звёздный проводник): C2 даёт +120 МС только
#: себе, а не активному персонажу отряда.
CRYO_MC_DD_KIT = replace(CRYO_MC_KIT, constellations={
    **CRYO_MC_KIT.constellations,
    2: Constellation(
        number=2,
        name="C2",
        buffs=(
            Buff(S.BASE_EM, 120.0, target=SELF, requires=(ON,),
                 source="C2 Крио ГГ (ДД): +120 МС себе"),
        ),
    ),
})

CMC_COMBO_DICT = {
    "cmc_ssw_mizuki_combo" : with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON, VV_CRYO)]),
        elemental("Навык (АТК)", "atk", 0.3851, "cryo", "skill",
                  [occ(5, OFF, DREAM, VV_CRYO,NOBLE),
                   occ(3, OFF, VV_CRYO)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST, VODYA_LEAD, VV_CRYO, SEVEN_SACRED, CATS_TAIL,NOBLE,TTDS_HALF)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST, VODYA_LEAD, VV_CRYO, SEVEN_SACRED, CATS_TAIL,NOBLE,TTDS_HALF)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST, VODYA_LEAD, VV_CRYO, SEVEN_SACRED, CATS_TAIL,NOBLE,TTDS_HALF)], kind="burst"),
    ),
    constellation_patches={
        4: {
            "Навык (АТК)": lambda s: replace(s, occurrences=[occ(9, OFF, DREAM, VV_CRYO,NOBLE),
                                                             occ(3, OFF, VV_CRYO)]),
        },
    },
),
    
    "cmc_ssw_vesna_combo" : with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON, VV_CRYO)]),
        elemental("Навык (АТК)", "atk", 0.3851, "cryo", "skill",
                  [occ(5, OFF, VV_CRYO,NOBLE),
                   occ(3, OFF, VV_CRYO)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST, VV_CRYO,NOBLE)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST, VV_CRYO,NOBLE)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST, VV_CRYO,NOBLE)], kind="burst"),
    ),
    constellation_patches={
        4: {
            "Навык (АТК)": lambda s: replace(s, occurrences=[occ(9, OFF, VV_CRYO,NOBLE),
                                                             occ(3, OFF, VV_CRYO)]),
        },
    },
),
    # ДД на поле через звёздный проводник: N2 P N2 N2 C N2 Q N2 N2, 8.7 с.
    # Окна отряда: все удары — под A4 Сахарозы (INST) и Изумрудной тенью (VV_CRYO).
    "cmc_sc_dd_combo": with_rotation(
    CRYO_MC_DD_KIT,
    sources=(
        elemental("Обычная атака 1 (крио)", "atk", NORMAL_MV[1] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(6, ON, INST, VV_CRYO,NOBLE)]),
        elemental("Обычная атака 2 (крио)", "atk", NORMAL_MV[2] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(6, ON, INST, VV_CRYO,NOBLE)]),
        elemental("Высокий удар в падении (крио)", "atk", HIGH_PLUNGE_MV + EVERPIERCING_FROST_ATK,
                  "cryo", "plunge", [occ(1, ON, INST, VV_CRYO,NOBLE)]),
        stellar_conduct("Заряженная атака — SC, 1", "atk", SPECIAL_CA_MV[0], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL)], kind="charged"),
        stellar_conduct("Заряженная атака — SC, 2", "atk", SPECIAL_CA_MV[1], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL)], kind="charged"),
        stellar_conduct("Взрыв — SC", "atk", BURST_SC_MV, "cryo",
                        [occ(5, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL)], kind="burst"),
    ),
),
    # ДД на поле через звёздный проводник, с навыком: E N2 N2 C Q N2, 6.4 с
    # (CMC_SC_DD_E_TIME). Окна и стаки — как в cmc_sc_dd_combo.
    "cmc_sc_dd_e_combo": with_rotation(
    CRYO_MC_DD_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON, INST, VV_CRYO)]),
        elemental("Обычная атака 1 (крио)", "atk", NORMAL_MV[1] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(3, ON, INST, VV_CRYO,NOBLE)]),
        elemental("Обычная атака 2 (крио)", "atk", NORMAL_MV[2] + EVERPIERCING_FROST_ATK,
                  "cryo", "normal", [occ(3, ON, INST, VV_CRYO,NOBLE)]),
        stellar_conduct("Заряженная атака — SC, 1", "atk", SPECIAL_CA_MV[0], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL, SUCROSE_PASSIVE)], kind="charged"),
        stellar_conduct("Заряженная атака — SC, 2", "atk", SPECIAL_CA_MV[1], "cryo",
                        [occ(1, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL, SUCROSE_PASSIVE)], kind="charged"),
        stellar_conduct("Взрыв — SC", "atk", BURST_SC_MV, "cryo",
                        [occ(5, ON, INST, VV_CRYO, TTDS_HALF, TTDS_FULL,NOBLE,SEVEN_SACRED,CATS_TAIL, SUCROSE_PASSIVE)], kind="burst"),
    ),
),
}


# --------------------------------------------------------------------------- #
#  Заполнитель времени ротации: дополнительные N2                              #
# --------------------------------------------------------------------------- #
_N2_SOURCES = ("Обычная атака 1 (крио)", "Обычная атака 2 (крио)")


def cmc_extra_n2(combo: Character, extra: int) -> Character:
    """Комбо + `extra` дополнительных N2 (N1 + N2).

    Доп. удары добавляются к вхождению N1/N2 с наибольшим числом тегов
    (окна баффов — те же, что у остальных N1/N2 комбо). Время ротации
    увеличивайте отдельно: extra × CMC_N2_TIME.
    """
    if extra <= 0:
        return combo
    sources = []
    for src in combo.sources:
        if src.name in _N2_SOURCES and src.occurrences:
            occs = list(src.occurrences)
            i = max(range(len(occs)), key=lambda k: len(occs[k].state))
            occs[i] = Occurrence(occs[i].state, occs[i].count + extra)
            src = replace(src, occurrences=occs)
        sources.append(src)
    assert sum(s.name in _N2_SOURCES for s in sources) == 2, "в комбо нет N1/N2"
    return replace(combo, sources=tuple(sources))


def cmc_filler_n2(rotation_time: float, min_time: float) -> int:
    """Сколько доп. N2 нужно, чтобы ротация была не короче min_time."""
    return max(0, math.ceil((min_time - rotation_time) / CMC_N2_TIME - 1e-9))


for _k in range(1, CMC_FILLER_MAX + 1):
    CMC_COMBO_DICT[f"cmc_sc_dd_combo_{_k}n2"] = cmc_extra_n2(
        CMC_COMBO_DICT["cmc_sc_dd_combo"], _k)

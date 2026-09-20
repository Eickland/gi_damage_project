"""
Крио ГГ (Крио Путешественник) — часть кита, НЕ зависящая от ротации/отряда.

Источники урона (в т.ч. по созвездиям) сюда не входят — подставляются
per-team через core.entities.with_rotation(), см. data/teams/*.py.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW
from ...core.sources import elemental, occ, stellar_swirl

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
            # mv зависит от ротации только у "Взрыв — SSW" по имени -
            # если в вашем отряде источник называется так же, патч сработает.
            patches={
                "Взрыв — SSW": lambda s: replace(s, mv=(1.1715 + 8 * 0.0586)),
            },
        ),
        4: Constellation(number=4, name="C4"),  # patches — per-team, если нужны
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
                temp(S.SSW_BONUS, 0.4, FROSTGLOW, target=TEAM,
                     source="+40% к урону звездных реакций на 15с после применения взрыва стихий"),
            ),
        ),
    },
    note="",
)

CMC_COMBO_DICT = {
    "cmc_ssw_combo" : with_rotation(
    CRYO_MC_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.6502, "cryo", "skill",
                  [occ(1, ON,)]),
        elemental("Навык (АТК)", "atk", 0.3851, "cryo", "skill",
                  [occ(5, OFF, DREAM), occ(8, OFF)]),
        stellar_swirl("Заряженная атака — SSW, 1", "atk", (1.105) + 1.40,
                      "cryo", [occ(1, ON, INST)], kind="charged"),
        stellar_swirl("Заряженная атака — SSW, 2", "atk", (1.428) + 1.40,
                      "cryo", [occ(1, ON, INST)], kind="charged"),
        stellar_swirl("Взрыв — SSW", "atk", (0.9924 + 8 * 0.0496), "cryo",
                      [occ(5, ON, INST)], kind="burst"),
    ),
    constellation_patches={
        4: {
            "Навык (АТК)": lambda s: replace(s, occurrences=[occ(9, OFF, DREAM), occ(3, OFF)]),
        },
    },
)
}
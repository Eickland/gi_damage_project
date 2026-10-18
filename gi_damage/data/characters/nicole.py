"""
Николь — пиро, катализатор. Чистый саппорт: только активация навыка
Revelation: Uncreated Light.

Grace of Kenosis — всему отряду (кроме самой Николь) +15% её АТК,
не больше 600. Methexis — Guidance of Theosis: ещё +300 АТК активному
персонажу, который провёл на поле 3 с (окно THEOSIS).

АТК Николь берётся вне поля и без её собственного Kenosis (бафф только
другим), поэтому зацикливания нет.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ
from ..tags import *

NICOLE_NAME = "Николь"

SKILL_MV = 2.4912
KENOSIS_RATIO = 0.15          # Grace of Kenosis: 15% АТК Николь
KENOSIS_CAP = 600.0           # … максимум 600
THEOSIS_ATK = 300.0           # Guidance of Theosis: ещё +300 АТК


def kenosis_bonus(ctx) -> float:
    return min(KENOSIS_CAP,
               KENOSIS_RATIO * ctx.stat(NICOLE_NAME, "atk", frozenset({OFF})))


NICOLE_KIT = Character(
    name=NICOLE_NAME,
    element="pyro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 342.0,
        S.ATK_PCT: 0.288,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        Buff(S.FLAT_ATK, kenosis_bonus, target=OTHERS,
             source="Grace of Kenosis: +15% АТК Николь (макс. 600)"),
        temp(S.FLAT_ATK, THEOSIS_ATK, THEOSIS, target=OTHERS,
             source="Methexis: Guidance of Theosis, ещё +300 АТК"),
    ),
    sources=(),
    note="Чистый саппорт.",
)

NICOLE_COMBO_DICT = {
    "support_e": with_rotation(
        NICOLE_KIT,
        sources=(
            elemental("Навык", "atk", SKILL_MV, "pyro", "skill", [occ(1, ON)]),
        ),
    ),
}

"""
Шилонен — гео, одноручный меч. Саппорт. Масштабируется от ЗАЩИТЫ.

Ротация: E, 1.2 с — дважды за ротацию отряда (до и после Сандроне), 2.4 с.

Навык «Скретч Йоуаль»: 3 сэмплера снижают сопротивление врагов
    к электро, крио, пиро, гидро и гео на 36% (C3: 45%).
    Условия активности сэмплеров не моделируются — снижение действует всегда.
    Урон выпада: 322.56% ЗЩ (гео, урон навыка).

C2  Микс Чиукуэ: гео-сэмплы всегда активны; персонажи отряда соответствующей
    стихии получают:
        гео  — +50% урона (dmg_bonus);
        пиро — +45% АТК;
        гидро — +45% макс. HP;
        крио — +60% крит. урона.
C3  снижение сопротивлений 45% вместо 36%.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ
from ..tags import *

XILONEN_NAME = "Шилонен"

# --------------------------------------------------------------------------- #
#  Константы                                                                   #
# --------------------------------------------------------------------------- #
SKILL_MV = 3.2256                     # выпад, доли ЗЩ
SKILL_CASTS = 2                       # E до и после Сандроне

RES_SHRED, RES_SHRED_C3 = 0.36, 0.45
SHRED_ELEMENTS = ("electro", "cryo", "pyro", "hydro", "geo")

C2_GEO_DMG = 0.50
C2_PYRO_ATK = 0.45
C2_HYDRO_HP = 0.45
C2_CRYO_CRIT_DMG = 0.60

XILONEN_TIME = 1.2 * SKILL_CASTS      # 2.4 с


def _for_element(element: str, value: float):
    """Значение баффа только для персонажей нужной стихии."""
    return lambda ctx: value if ctx.recipient_element() == element else 0.0


XILONEN_KIT = Character(
    name=XILONEN_NAME,
    element="geo",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_DEF: 930.0,
        S.CRIT_VALUE: 0.6,            # 5% КШ / 50% КУ
    },
    buffs=tuple(
        Buff(f"res_reduction.{el}", RES_SHRED, target=TEAM,
             source=f"Скретч Йоуаль: −36% сопротивления ({el})")
        for el in SHRED_ELEMENTS
    ),
    sources=(),
    constellations={
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(S.DMG_BONUS, _for_element("geo", C2_GEO_DMG), target=TEAM,
                     source="C2 Шилонен: гео персонажам +50% урона"),
                Buff(S.ATK_PCT, _for_element("pyro", C2_PYRO_ATK), target=TEAM,
                     source="C2 Шилонен: пиро персонажам +45% АТК"),
                Buff(S.HP_PCT, _for_element("hydro", C2_HYDRO_HP), target=TEAM,
                     source="C2 Шилонен: гидро персонажам +45% HP"),
                # Оба ключа: crit_value — для режимов по крит-вэлью (balance),
                # crit_dmg — для expected/always.
                Buff(S.CRIT_VALUE, _for_element("cryo", C2_CRYO_CRIT_DMG), target=TEAM,
                     source="C2 Шилонен: крио персонажам +60% крит. урона"),
                Buff(S.CRIT_DMG, _for_element("cryo", C2_CRYO_CRIT_DMG), target=TEAM,
                     source="C2 Шилонен: крио персонажам +60% крит. урона"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            buffs=tuple(
                Buff(f"res_reduction.{el}", RES_SHRED_C3 - RES_SHRED, target=TEAM,
                     source=f"C3 Шилонен: снижение сопротивления ({el}) до 45%")
                for el in SHRED_ELEMENTS
            ),
        ),
    },
    note="Гео саппорт: снижение сопротивлений.",
)

XILONEN_COMBO_DICT = {
    # E дважды за ротацию (до и после Сандроне)
    "ee": with_rotation(
        XILONEN_KIT,
        sources=(
            elemental("Скретч Йоуаль — выпад", "def", SKILL_MV, "geo", "skill",
                      [occ(SKILL_CASTS, ON)]),
        ),
    ),
}

"""
Отряд Мидзуки/Одетта/Крио ГГ/Сахароза,
Короткая ротация с 3 проками A4 Мидзуки и с 3 проками C1 Мидзуки,

Мидзуки/Крио ГГ/Одетта заведены через общий кит (data/kits/) + with_rotation():
статы/баффы/патчи по созвездиям — общие с другими отрядами, здесь задаётся
только КОНКРЕТНАЯ ротация (occurrences/mv). Сахароза встречается только в этом
отряде, поэтому оставлена целиком как обычно.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — на случай локальных patches=

from ...core.buffs import OTHERS, temp
from ...core.entities import Character, with_rotation
from ...core.sources import elemental, occ, stellar_swirl
from ...core.stats import S
from ..characters.cryo_mc import CMC_COMBO_DICT
from ..characters.mizuki import MIZUKI_COMBO_DICT
from ..characters.odette import ODETTE_COMBO_DICT
from ..characters.sucrose import SUCROSE_COMBO_DICT
from ..tags import DREAM, FROSTGLOW, INST, OFF, ON

# =========================================================================== #
#  Мидзуки — анемо, main dps                                                  #
# =========================================================================== #
MIZUKI = MIZUKI_COMBO_DICT["mizuki_short_combo"]

# =========================================================================== #
#  Крио ГГ (Крио Путешественник)                                              #
# =========================================================================== #
CRYO_MC = CMC_COMBO_DICT["cmc_ssw_combo"]

# =========================================================================== #
#  Одетта                                                                     #
# =========================================================================== #
ODETTE = ODETTE_COMBO_DICT["odette_short_mizuki_combo_no_burst"]

# =========================================================================== #
#  Сахароза (только в этом отряде — свой кит не заводим)                      #
# =========================================================================== #
SUCROSE = SUCROSE_COMBO_DICT["no_burst_combo"]


ALL = {c.name: c for c in (MIZUKI, CRYO_MC, ODETTE, SUCROSE)}
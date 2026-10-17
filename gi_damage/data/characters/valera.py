"""
Валера — электро, одноручник. Чистый саппорт. Всегда в звёздном проводнике
(Radiance: Stellar-Conduct). Ротация: E Q CA (особая заряженная атака), 2.4 с.

Все баффы постоянные, Impact Momentum всегда хватает (40 — с навыка).

Offensive Directive (15 стаков после особой заряженной атаки):
    электро урон звёздного проводника АКТИВНОГО персонажа (обычные, заряженные,
    в падении, навык, взрыв) получает доп. базовый урон
        АТК Валеры × (131.33% + 0.9% × Impact Momentum)
    Это «Additional Increase» звёздного проводника (как бафф Водяницы):
        Итог = (База + доп.) × Сопр. × Крит × Возвышение.
    Бафф работает только в окне OFFENSIVE_DIRECTIVE — этим тегом отмечаются
    удары, которые тратят стаки (не больше 15 за ротацию).

ВНИМАНИЕ: множители взрыва стихии в задании не даны — BURST_MV и
BURST_SHELL_MV стоят 0.0, впишите значения.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ

VALERA_NAME = "Валера"

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
CA_MV = 1.9822                # обычная заряженная атака (физ.)
MORTAR_MV = 4.1256            # Direct-Fire Mortar: Point-Blank Bombardment
SKILL_MV = 2.988              # Active Defense: Bastion Charge
BURST_MV = 0.0                # TODO: урон взрыва при применении (не дан)
BURST_SHELL_MV = 0.0          # TODO: урон снарядов Thunderburst Shell (не дан)
BURST_SHELL_HITS = 6          # раз в 3.5 с

OD_STACKS = 15                # стаков Offensive Directive
OD_ELECTRO_ATK = 0.4378       # вне Radiance: +43.78% АТК Валеры (для справки)
OD_SC_ATK = 1.3133            # в Radiance: +131.33% АТК Валеры
IMPACT_MOMENTUM = 100          # тратится особой заряженной атакой
A1_SC_PER_MOMENTUM = 0.009    # Into the Breach: +0.9% АТК за 1 Impact Momentum (Radiance)
A1_ELECTRO_PER_MOMENTUM = 0.003

C2_EM = 100.0                 # C2: +100 МС отряду
C6_DMG = 1.00                 # C6: +100% урона мортиры и снарядов взрыва
C6_ELECTRO_CR = 0.10          # C6: +10% КШ электро урона по цели
C6_SC_CD = 0.40               # C6: +40% КУ электро урона звёздного проводника

#: Тег источников, усиливаемых C6 (мортира и снаряды взрыва)
VALERA_C6 = "valera_c6"

#: Доп. базовый урон за один стак Offensive Directive, в долях АТК Валеры
OD_SC_TOTAL = OD_SC_ATK + A1_SC_PER_MOMENTUM * IMPACT_MOMENTUM   # 1.6733


def offensive_directive_bonus(ctx) -> float:
    """АТК Валеры (вне поля) × (131.33% + 0.9% × 40)."""
    return OD_SC_TOTAL * ctx.stat(VALERA_NAME, "atk", frozenset({OFF}))


VALERA_KIT = Character(
    name=VALERA_NAME,
    element="electro",
    weapon_type="sword",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 255.0,
        S.ATK_PCT: 0.24,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        # Только электро урон звёздного проводника, только активному персонажу
        # и только в ударах, помеченных OFFENSIVE_DIRECTIVE.
        Buff(f"{S.FLAT_BASE_DMG}.electro.stellar_conduct", offensive_directive_bonus,
             target=OTHERS, requires=(ON, OFFENSIVE_DIRECTIVE),
             source="Offensive Directive + Into the Breach: +167.33% АТК Валеры "
                    "(доп. базовый урон SC)"),
    ),
    sources=(),
    constellations={
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.BASE_EM, C2_EM, target=TEAM,
                     source="C2 Валеры: +100 МС отряду"),
            ),
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff(f"{S.DMG_BONUS}.{VALERA_C6}", C6_DMG, target=SELF,
                     source="C6 Валеры: +100% урона мортиры и снарядов взрыва"),
                Buff("crit_value.electro", C6_ELECTRO_CR * 2, target=TEAM,
                     source="C6 Валеры: +10% КШ электро урона по цели"),
                Buff("crit_value.electro.stellar_conduct", C6_SC_CD, target=TEAM,
                     source="C6 Валеры: +40% КУ электро урона звёздного проводника"),
            ),
        ),
    },
    note="Чистый саппорт.",
)

_VALERA_TAGS = (ON, NOBLE)

VALERA_COMBO_DICT = {
    # E Q CA (особая заряженная атака), 2.4 с; снаряды взрыва — вне поля.
    "support_eq_ca": with_rotation(
        VALERA_KIT,
        sources=(
            elemental("Навык", "atk", SKILL_MV, "electro", "skill",
                      [occ(1, *_VALERA_TAGS)]),
            elemental("Взрыв стихии", "atk", BURST_MV, "electro", "burst",
                      [occ(1, *_VALERA_TAGS)]),
            elemental("Особая заряженная атака (мортира)", "atk", MORTAR_MV, "electro",
                      "charged", [occ(1, *_VALERA_TAGS)], extra_tags=(VALERA_C6,)),
            elemental("Снаряды Thunderburst Shell", "atk", BURST_SHELL_MV, "electro",
                      "burst", [occ(BURST_SHELL_HITS, OFF, NOBLE)], extra_tags=(VALERA_C6,)),
        ),
    ),
}

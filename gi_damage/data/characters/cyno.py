"""
Сайно — играет только в отрядах звёздного проводника
(всегда действует Radiance: Stellar-Conduct).

C1 — базовая линия (созвездие выдаётся бесплатно), поэтому сборки по
умолчанию собираются с constellation=1.

Звёздный урон Сайно — только «Duststalker Bolts - Starsame»
(A1 Featherfall Judgment + C6). Всё остальное — обычный электро урон.

Допущение: «+600% МС» от A4 к Starsame складывается с «200% АТК» ВНУТРИ
базы прямого урона (Attribute × Multiplier), т.е. дальше умножается на
(1 + Base DMG Increase) и на (1 + 6·МС/(МС+2000) + бонус SC). Так же
«+150% МС» к обычным атакам — это прибавка к базе до бонуса урона.
Реализовано через DamageSource.extra_scaling.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_conduct

# --------------------------------------------------------------------------- #
#  Множители талантов (в долях)                                                #
# --------------------------------------------------------------------------- #
SKILL_MV = 2.3472             # Secret Rite: Chasmic Soulfarer — обычный навык
MORTUARY_RITE_MV = 2.8224     # навык в состоянии Pactsworn Pathclearer

NA_MV = {1: 1.5475, 2: 1.6302, 3: 2.0683, 4: 1.0219, 5: 2.5865}  # 4-й удар — 2 инстанса
CA_MV = 1.9975
BURST_EM = 100.0              # МС в Pactsworn Pathclearer

JUDICATION_BONUS = 0.35       # A1: +35% урона навыка при Judication
STARSAME_ATK = 2.00           # Duststalker Bolt - Starsame: 200% АТК
STARSAME_EM = 6.00            # A4: +600% МС
BOLT_ATK = 1.00               # обычный Duststalker Bolt (без Radiance) — для справки
BOLT_EM = 2.50
NA_EM = 1.50                  # A4: обычные атаки в Pathclearer +150% МС

TWR_EM = 200.0                # C1 Radiance: Together We Rise, +200 МС
C2_ELECTRO_BONUS = 0.10 * 5   # C2: +10% электро урона × 5 стаков
C2_SC_BONUS = 0.16 * 5        # C2: +16% урона звёздного проводника × 5 стаков

#: Стаки «полярности» для звёздного проводника Сайно (см. formulas.stellar_conduct_multiplier).
#: Взято как у Сандроне (основной персонаж на поле) — поправьте при необходимости.
CYNO_POLAR_STACKS = 7

#: Тег источника для +35% Judication (бафф «dmg_bonus.judication»)
JUDICATION = "judication"


CYNO_KIT = Character(
    name="Сайно",
    element="electro",
    weapon_type="polearm",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 318.0,
        # 5% КШ × 2 + 50% КУ + 38.4% КУ с возвышения
        S.CRIT_VALUE: 0.6 + 0.384,
    },
    buffs=(
        Buff(S.BASE_EM, BURST_EM, target=SELF, requires=(PACTSWORN,),
             source="Pactsworn Pathclearer: +100 МС"),
        Buff(f"{S.DMG_BONUS}.{JUDICATION}", JUDICATION_BONUS, target=SELF,
             source="Featherfall Judgment: +35% урона навыка при Judication"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                # Сам Сайно получает Together We Rise при входе в Pathclearer
                Buff(S.BASE_EM, TWR_EM, target=SELF, requires=(PACTSWORN,),
                     source="C1 Together We Rise: +200 МС (Сайно)"),
                # Переходит к следующему активному персонажу — пока никуда не добавлен
                temp(S.BASE_EM, TWR_EM, TOGETHER_WE_RISE, target=OTHERS,
                     source="C1 Together We Rise: +200 МС (входящему персонажу)"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                # Полные стаки сразу
                Buff("dmg_bonus.electro", C2_ELECTRO_BONUS, target=SELF,
                     requires=(PACTSWORN,),
                     source="C2: +50% электро урона (5 стаков)"),
                Buff(S.SC_BONUS, C2_SC_BONUS, target=SELF, requires=(PACTSWORN,),
                     source="C2: +80% урона звёздного проводника (Together We Rise, 5 стаков)"),
                # Для других носителей Together We Rise — пока никуда не добавлен
                temp(S.SC_BONUS, C2_SC_BONUS, TOGETHER_WE_RISE, target=OTHERS,
                     source="C2: +80% урона звёздного проводника (Together We Rise, 5 стаков)"),
            ),
        ),
        6: Constellation(number=6, name="C6"),
    },
    note="Только отряды звёздного проводника.",
)


def _na(name: str, mv: float, count: float, tags) -> object:
    """Обычная атака в Pathclearer: электро, +150% МС к базе (A4)."""
    return elemental(name, "atk", mv, "electro", "normal", [occ(count, *tags)],
                     extra_scaling=(("em", NA_EM),))


def _starsame(name: str, count: float, tags) -> object:
    return stellar_conduct(name, "atk", STARSAME_ATK, "electro",
                           [occ(count, *tags)], kind="skill",
                           extra_scaling=(("em", STARSAME_EM),),
                           polar_stacks=CYNO_POLAR_STACKS)


#: Все временные окна отряда Одетта/Алеша/Диона, в которых находится Сайно.
#: Расставляйте по ударам, как нужно.
_SC_TEAM_TAGS = (ON, PACTSWORN, CATS_TAIL, NOBLE)

CYNO_COMBO_DICT = {
    # Q, E, затем 3 × (N2, CA, N4, E с Judication). 15 с.
    "sc_combo": with_rotation(
        CYNO_KIT,
        sources=(
            _na("Pathclearer — 1-й удар", NA_MV[1], 3 * 2, _SC_TEAM_TAGS),
            _na("Pathclearer — 2-й удар", NA_MV[2], 3 * 2, _SC_TEAM_TAGS),
            _na("Pathclearer — 3-й удар", NA_MV[3], 3 * 1, _SC_TEAM_TAGS),
            _na("Pathclearer — 4-й удар (2 инстанса)", NA_MV[4], 3 * 2, _SC_TEAM_TAGS),
            elemental("Pathclearer — заряженная атака", "atk", CA_MV, "electro", "charged",
                      [occ(3, *_SC_TEAM_TAGS)]),
            elemental("Mortuary Rite", "atk", MORTUARY_RITE_MV, "electro", "skill",
                      [occ(1, *_SC_TEAM_TAGS)]),
            elemental("Mortuary Rite (Judication)", "atk", MORTUARY_RITE_MV, "electro", "skill",
                      [occ(3, *_SC_TEAM_TAGS)], extra_tags=(JUDICATION,)),
            _starsame("Duststalker Bolt - Starsame (A1)", 3 * 2, _SC_TEAM_TAGS),
            _starsame("Duststalker Bolt - Starsame (A1)", 3 * 1, (ON, PACTSWORN)),
        ), # type: ignore
        constellation_sources={
            # Q даёт 4 стака, первый Judication ещё 4 → максимум 8 за Pathclearer.
            # Сайно всегда под Together We Rise (C1), поэтому все — Starsame.
            6: (_starsame("C6: Duststalker Bolt - Starsame", 8, _SC_TEAM_TAGS),),
        }, # type: ignore
    ),
}

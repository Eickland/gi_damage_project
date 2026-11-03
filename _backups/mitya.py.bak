"""
Митя — электро, катализатор. Гибрид (ДД / саппорт), пока — САППОРТ:
навык нажатием → Ядро обнаружения в «Steady State».

Всегда в отрядах звёздного проводника. Все баффы считаются постоянными,
бонус Steady State (A1) — сразу полный.

Комбо саппорта (17 ударов): 4 электро + 13 звёздного проводника.
    электро:  1 × навык нажатием (163.3% АТК)
              3 × удар ядра Steady State (129.6% АТК)
    SC:       ядро поглощает маяки сверх максимума (144% МС за удар)
              + подрыв ядра в конце: 165.6% МС за каждый маяк, который держит Митя
              C0: 10 поглощений + 3 маяка подрыва;  C1 (макс. 5 маяков): 8 + 5.

Допущения (в задании не указано):
  * максимум маяков без C1 — 3 (C1 поднимает до 5);
  * подрыв считается как N инстансов по 165.6% МС (N = число маяков);
  * C4: 13 поглощённых маяков → 2 доп. удара по 300% МС.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_conduct

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
TAP_SKILL_MV = 1.633                 # навык нажатием, АТК
HOLD_SKILL_MV = 2.3328               # навык удержанием, АТК (режим ДД)
CORE_MV = 1.296                      # удар ядра Steady State, АТК
CORE_CONSUME_EM = 1.44               # поглощение маяка ядром, МС (SC)
CORE_DETONATION_EM = 1.656           # подрыв ядра, МС за маяк (SC)
GRADIENT_DETONATION_MV = 3.024       # особая заряженная атака, АТК (режим ДД)
GRADIENT_DETONATION_SC_EM = 4.032    # она же — SC за маяк, МС (режим ДД)
C4_EM = 3.00                         # C4: 300% МС за каждые 5 поглощённых маяков

MAX_BEACONS = {0: 4, 1: 5}           # максимум маяков: без C1 / с C1
A1_EM_PER_BEACON = 30.0              # Baseline Stress Test: +30 МС отряду за маяк
A4_CRIT_RATE = 0.05 * 4              # Explosive Reagent: +5% КШ × 4 стака
A3_BASE_INC_PER_EM = 0.00028         # Stellar Jubilee: +0.028% Base SC DMG за 1 МС
A3_BASE_INC_CAP = 0.14               # … максимум 14%
C1_CRIT_DMG = 0.40                   # C1: +40% КУ активному персонажу
C2_RES_SHRED = 0.20                  # C2: -20% крио и электро сопротивления
C2_STEADY_EM = 123.0                 # C2: Steady State, +123 МС отряду
C6_CORE_MULT = 1.15                  # C6: ядро Steady State наносит 115% урона
C6_SC_ELEVATION = 0.20               # C6: возвышение урона реакции SC +20% отряду

#: Количество ударов в комбо саппорта
ELECTRO_CORE_HITS = 3
SC_HITS = 13
C4_HITS = SC_HITS // 5               # 2

#: Стаки «полярности» для звёздного проводника Мити (вне поля)
MITYA_POLAR_STACKS = 6

MITYA_NAME = "Митя"


def _mitya_em(ctx) -> float:
    """МС Мити вне поля (для баффов, зависящих от его МС)."""
    return ctx.stat(MITYA_NAME, "em", frozenset({OFF}))


MITYA_KIT = Character(
    name=MITYA_NAME,
    element="electro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 263.0,
        S.BASE_EM: 100.0,
        # 5% КШ × 2 + 50% КУ + 38.4% КУ с возвышения
        S.CRIT_VALUE: 0.6 + 0.384,
    },
    buffs=(
        Buff(S.BASE_EM, A1_EM_PER_BEACON * MAX_BEACONS[0], target=TEAM,
             source="Baseline Stress Test: +30 МС отряду за маяк (3 маяка)"),
        Buff(S.CRIT_VALUE, A4_CRIT_RATE * 2, target=SELF,
             source="Explosive Reagent: +20% КШ (4 стака)"),
        Buff(S.SC_BASE_INC,
             lambda ctx: min(A3_BASE_INC_CAP, A3_BASE_INC_PER_EM * _mitya_em(ctx)),
             target=TEAM,
             source="Stellar Jubilee: +0.028% базового урона SC за 1 МС Мити (макс. 14%)"),
    ),
    # «core» — множитель урона ядра Steady State (C6 поднимает до 1.15)
    multipliers={"core": lambda stats: 1.0},
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                # Ещё 2 маяка (3 → 5) для A1
                Buff(S.BASE_EM, A1_EM_PER_BEACON * (MAX_BEACONS[1] - MAX_BEACONS[0]),
                     target=TEAM, source="C1: +2 маяка → ещё +60 МС отряду (A1)"),
                Buff(S.CRIT_VALUE, C1_CRIT_DMG, target=TEAM, requires=(ON,),
                     source="C1 Мити: +40% КУ активному персонажу"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff("res_reduction.cryo", C2_RES_SHRED, target=TEAM,
                     source="C2 Мити: -20% крио сопротивления"),
                Buff("res_reduction.electro", C2_RES_SHRED, target=TEAM,
                     source="C2 Мити: -20% электро сопротивления"),
                Buff(S.BASE_EM, C2_STEADY_EM, target=TEAM,
                     source="C2 Мити (Steady State): +123 МС отряду"),
            ),
        ),
        4: Constellation(number=4, name="C4"),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("elevation.stellar_conduct", C6_SC_ELEVATION, target=TEAM,
                     source="C6 Мити: +20% возвышения урона звёздного проводника"),
            ),
            multipliers={"core": lambda stats: C6_CORE_MULT},
        ),
    },
    note="Пока только саппорт (Steady State).",
)

_MITYA_TAGS = (OFF,)

MITYA_COMBO_DICT = {
    "support_steady": with_rotation(
        MITYA_KIT,
        sources=(
            elemental("Навык нажатием", "atk", TAP_SKILL_MV, "electro", "skill",
                      [occ(1, ON)]),
            elemental("Ядро Steady State", "atk", CORE_MV, "electro", "skill",
                      [occ(ELECTRO_CORE_HITS, *_MITYA_TAGS)], multipliers=("core",)),
            stellar_conduct("Ядро — поглощение маяка (SC)", "em", CORE_CONSUME_EM, "electro",
                            [occ(SC_HITS - MAX_BEACONS[0], *_MITYA_TAGS)], kind="skill",
                            multipliers=("core",), polar_stacks=MITYA_POLAR_STACKS),
            stellar_conduct("Ядро — подрыв маяков (SC)", "em", CORE_DETONATION_EM, "electro",
                            [occ(MAX_BEACONS[0], *_MITYA_TAGS)], kind="skill",
                            multipliers=("core",), polar_stacks=MITYA_POLAR_STACKS),
        ),
        constellation_patches={
            # 5 маяков: подрыв на 5, поглощений на 2 меньше (всего по-прежнему 13)
            1: {
                "Ядро — поглощение маяка (SC)": lambda s: replace(
                    s, occurrences=[occ(SC_HITS - MAX_BEACONS[1], *_MITYA_TAGS)]),
                "Ядро — подрыв маяков (SC)": lambda s: replace(
                    s, occurrences=[occ(MAX_BEACONS[1], *_MITYA_TAGS)]),
            },
        },
        constellation_sources={
            4: (
                stellar_conduct("C4: удар за 5 поглощённых маяков (SC)", "em", C4_EM,
                                "electro", [occ(C4_HITS, *_MITYA_TAGS)], kind="skill",
                                polar_stacks=MITYA_POLAR_STACKS),
            ),
        },
    ),
}

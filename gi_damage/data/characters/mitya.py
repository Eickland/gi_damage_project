"""
Митя — электро, катализатор. Гибрид: САППОРТ или ДД на поле.

САППОРТ — навык нажатием → Ядро обнаружения в «Steady State»
-------------------------------------------------------------
Всегда в отрядах звёздного проводника. Все баффы считаются постоянными,
бонус Steady State (A1) — сразу полный.

Комбо саппорта (17 ударов): 4 электро + 13 звёздного проводника.
    электро:  1 × навык нажатием (163.3% АТК)
              3 × удар ядра Steady State (129.6% АТК)
    SC:       ядро поглощает маяки сверх максимума (144% МС за удар)
              + подрыв ядра в конце: 165.6% МС за каждый маяк, который держит Митя
              C0: 10 поглощений + 3 маяка подрыва;  C1 (макс. 5 маяков): 8 + 5.
    C6: ядро (все удары из кармана) наносит 115% исходного урона.

ДД — режим перегрузки, Митя на поле (MITYA_DD_KIT, mitya_dd_rotation)
---------------------------------------------------------------------
Комбо: hE → CA Q CA CA (10.2 с).
    * A1 (+30 МС отряду за маяк, т.е. +120 / +180 с C1) НЕ работает.
    * Заряженные атаки «Имплозия превращения»: 1 израсходованный Маячок
      превращения = 1 удар звёздного проводника, 403.2% МС (C5: 476% МС).
      C0 — 13 ударов, C1+ — 16.
    * Offensive Directive Валеры тратится на эти удары: C0 — 13 стаков,
      C1+ — 15 (последний, 16-й удар — без стака).
    * C2: вместо +123 МС отряду — +234 МС активному персонажу (постоянно).
    * C6: при расходе маяка с шансом 34% создаётся новый маяк. Новые маяки
      тоже могут создать маяк, поэтому ожидаемое число ударов —
      геометрический ряд  N · (1 + p + p² + …) = N / (1 − p) = 16 / 0.66 ≈ 24.24.
      Стаков Offensive Directive по-прежнему 15, остальные удары — без него.
      +20% возвышения урона SC отряду — общее для обоих режимов.
    * Взрыв «Анализ: Теория превращения»: 600.48% АТК + 1200.96% МС —
      обычный электро урон взрыва (не звёздный проводник), считается двумя
      источниками (АТК-часть и МС-часть), формула линейна, сумма точна.

Допущения (в задании не указано):
  * саппорт: максимум маяков без C1 — 4 (C1 поднимает до 5);
  * саппорт: подрыв считается как N инстансов по 165.6% МС (N = число маяков);
  * саппорт: C4 — 13 поглощённых маяков → 2 доп. удара по 300% МС;
  * ДД: стаки полярности у ударов имплозии — MITYA_DD_POLAR_STACKS;
  * ДД: C4 (поглощение маяков ядром) в режиме ДД не работает;
  * ДД: удар самой заряженной атаки по АТК (GRADIENT_DETONATION_MV) не считается —
    только удары SC по маякам.
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
GRADIENT_DETONATION_MV = 3.024       # особая заряженная атака, АТК (режим ДД, не используется)
GRADIENT_DETONATION_SC_EM = 4.032    # Имплозия превращения — SC за маяк, МС (режим ДД)
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

# --- режим ДД (перегрузка) -------------------------------------------------- #
IMPLOSION_EM = GRADIENT_DETONATION_SC_EM   # 403.2% МС за маяк
C5_IMPLOSION_EM = 4.76                     # C5: 476% МС за маяк
DD_BURST_ATK_MV = 6.0048                   # взрыв: 600.48% АТК
DD_BURST_EM_MV = 12.0096                   # взрыв: 1200.96% МС
DD_HITS = {0: 13, 1: 16}                   # ударов имплозии: C0 / C1+
DD_OD_STACKS = {0: 13, 1: 15}              # стаков Offensive Directive Валеры
C2_DD_ACTIVE_EM = 234.0                    # C2 (ДД): +234 МС активному персонажу
C6_BEACON_CHANCE = 0.34                    # C6 (ДД): шанс нового маяка
#: Ожидаемое число ударов на один исходный маяк: 1 + p + p² + … = 1 / (1 − p)
C6_HIT_FACTOR = 1.0 / (1.0 - C6_BEACON_CHANCE)
DD_TIME = 10.2                             # hE + CA Q CA CA, секунды
#: Стаки «полярности» для ударов имплозии (Митя на поле, отряд электро SC)
MITYA_DD_POLAR_STACKS = 6

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


# --------------------------------------------------------------------------- #
#  Баффы                                                                       #
# --------------------------------------------------------------------------- #
_A1_TEAM_EM = Buff(S.BASE_EM, A1_EM_PER_BEACON * MAX_BEACONS[0], target=TEAM,
                   source="Baseline Stress Test: +30 МС отряду за маяк (4 маяка)")

_COMMON_BUFFS = (
    Buff(S.CRIT_VALUE, A4_CRIT_RATE * 2, target=SELF,
         source="Explosive Reagent: +20% КШ (4 стака)"),
    Buff(S.SC_BASE_INC,
         lambda ctx: min(A3_BASE_INC_CAP, A3_BASE_INC_PER_EM * _mitya_em(ctx)),
         target=TEAM,
         source="Stellar Jubilee: +0.028% базового урона SC за 1 МС Мити (макс. 14%)"),
)

_C1_ACTIVE_CD = Buff(S.CRIT_VALUE, C1_CRIT_DMG, target=TEAM, requires=(ON,),
                     source="C1 Мити: +40% КУ активному персонажу")
_C2_SHRED = (
    Buff("res_reduction.cryo", C2_RES_SHRED, target=TEAM,
         source="C2 Мити: -20% крио сопротивления"),
    Buff("res_reduction.electro", C2_RES_SHRED, target=TEAM,
         source="C2 Мити: -20% электро сопротивления"),
)
_C6_ELEVATION = Buff("elevation.stellar_conduct", C6_SC_ELEVATION, target=TEAM,
                     source="C6 Мити: +20% возвышения урона звёздного проводника")


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
    buffs=(_A1_TEAM_EM,) + _COMMON_BUFFS,
    # «core» — множитель урона ядра Steady State (C6 поднимает до 1.15)
    multipliers={"core": lambda stats: 1.0},
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                # Ещё 1 маяк (4 → 5) для A1
                Buff(S.BASE_EM, A1_EM_PER_BEACON * (MAX_BEACONS[1] - MAX_BEACONS[0]),
                     target=TEAM, source="C1: +1 маяк → ещё +30 МС отряду (A1)"),
                _C1_ACTIVE_CD,
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=_C2_SHRED + (
                Buff(S.BASE_EM, C2_STEADY_EM, target=TEAM,
                     source="C2 Мити (Steady State): +123 МС отряду"),
            ),
        ),
        4: Constellation(number=4, name="C4"),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(_C6_ELEVATION,),
            multipliers={"core": lambda stats: C6_CORE_MULT},
        ),
    },
    note="Саппорт (Steady State).",
)

#: Митя в режиме ДД (перегрузка): без A1, свои C1/C2/C5/C6.
MITYA_DD_KIT = replace(
    MITYA_KIT,
    default_field=ON,
    buffs=_COMMON_BUFFS,
    multipliers={},
    constellations={
        1: Constellation(number=1, name="C1", buffs=(_C1_ACTIVE_CD,)),
        2: Constellation(
            number=2,
            name="C2",
            buffs=_C2_SHRED + (
                Buff(S.BASE_EM, C2_DD_ACTIVE_EM, target=TEAM, requires=(ON,),
                     source="C2 Мити (перегрузка): +234 МС активному персонажу"),
            ),
        ),
        4: Constellation(number=4, name="C4"),
        5: Constellation(number=5, name="C5"),
        6: Constellation(number=6, name="C6", buffs=(_C6_ELEVATION,)),
    },
    note="ДД на поле (режим перегрузки).",
)

_MITYA_TAGS = (OFF,)

IMPLOSION_NAME = "Имплозия превращения (SC)"


def _implosion_occ(total: float, od: int, hit_tags, od_tags):
    """Первые `od` ударов тратят стаки Offensive Directive, остальные — нет."""
    od = min(od, total) # type: ignore
    out = [occ(od, *od_tags)] if od > 0 else []
    if total - od > 1e-9:
        out.append(occ(total - od, *hit_tags))
    return out


def mitya_dd_rotation(hit_tags=(ON,), hold_tags=(ON,), burst_tags=None,
                      polar_stacks: int = MITYA_DD_POLAR_STACKS) -> Character:
    """Митя-ДД под конкретную ротацию: hE → CA Q CA CA.

    hit_tags   — теги ударов имплозии (OFFENSIVE_DIRECTIVE добавляется сам
                 к первым 13 / 15 ударам);
    hold_tags  — теги навыка удержанием;
    burst_tags — теги взрыва (по умолчанию = hit_tags).
    """
    hit_tags = tuple(hit_tags)
    burst_tags = tuple(burst_tags) if burst_tags is not None else hit_tags
    od_tags = hit_tags + (OFFENSIVE_DIRECTIVE,)

    def occs(total, od):
        return _implosion_occ(total, od, hit_tags, od_tags)

    c6_total = DD_HITS[1] * C6_HIT_FACTOR
    return with_rotation(
        MITYA_DD_KIT,
        sources=(
            elemental("Навык удержанием", "atk", HOLD_SKILL_MV, "electro", "skill",
                      [occ(1, *hold_tags)]),
            stellar_conduct(IMPLOSION_NAME, "em", IMPLOSION_EM, "electro",
                            occs(DD_HITS[0], DD_OD_STACKS[0]), kind="charged",
                            polar_stacks=polar_stacks),
            elemental("Взрыв стихии (АТК)", "atk", DD_BURST_ATK_MV, "electro", "burst",
                      [occ(1, *burst_tags)]),
            elemental("Взрыв стихии (МС)", "em", DD_BURST_EM_MV, "electro", "burst",
                      [occ(1, *burst_tags)]),
        ),
        constellation_patches={
            1: {IMPLOSION_NAME: lambda s: replace(
                s, occurrences=occs(DD_HITS[1], DD_OD_STACKS[1]))},
            5: {IMPLOSION_NAME: lambda s: replace(s, mv=C5_IMPLOSION_EM)},
            6: {IMPLOSION_NAME: lambda s: replace(
                s, occurrences=occs(c6_total, DD_OD_STACKS[1]))},
        },
    )


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
            # 5 маяков: подрыв на 5, поглощений на 1 меньше (всего по-прежнему 13)
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
    # ДД: Одетта EE / Яэ EEE / Митя hE CA / Валера E CA Q / Митя CA Q CA.
    # Все удары после Валеры — в окне «Знати» Валеры.
    "dd_overload_valera": mitya_dd_rotation(
        hit_tags=(ON, NOBLE), hold_tags=(ON,), burst_tags=(ON, NOBLE)),
    # ДД: Одетта EE / Валера E CA Q / Сахароза EdQ / Митя hE CA Q CA /
    #     Сахароза Ed / Митя CA — все удары Мити под баффами Сахарозы
    #     (A1 +50 МС, A4 +20% её МС, «Тайные истории драконоборцев» +48% АТК)
    #     и Изумрудной тенью (электро).
    "dd_overload_sucrose": mitya_dd_rotation(
        hit_tags=(ON, NOBLE, INST, SUCROSE_PASSIVE, VV_ELECTRO, TTDS_FULL),
        hold_tags=(ON, NOBLE, INST, SUCROSE_PASSIVE, VV_ELECTRO, TTDS_FULL)),
}

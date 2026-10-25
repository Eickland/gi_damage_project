"""
Нефер — дендро, катализатор. ДД лунных бутонов (Moonsign).

Ротация: (E sCA sCA sCA) × 2, 8.5 с
    E    — Senet Strategy: 137.49% АТК + 274.98% МС (дендро)
    sCA  — Phantasm Performance:
           сама Нефер — 2 удара (дендро, АТК + МС);
           тени — 3 удара прямых лунных бутонов (только МС).

Баффы (постоянные; Ascendant Gleam активен):
    A1  Veil of Falsehood — всегда VEIL_STACKS = 3 стака (C2: 5): урон Phantasm
        Performance ×(1 + 8% × стаки) — множитель "veil" на всех её ударах;
        при 3 стаках +100 МС
    Moonsign Benediction: +0.0175% базового урона лунных бутонов за 1 МС (макс. 14%) отряду
    C1  лунные бутоны Phantasm Performance: +60% МС к множителю удара
        (складывается с множителем навыка: тень 172.8% → 232.8% МС; дальше
        умножается на Base DMG Increase, скобку с МС и Veil)
    C2  всегда 5 стаков Veil: урон Phantasm Performance ×1.40, +200 МС вместо +100
    C3  новые множители
    C4  −20% дендро сопротивления
    C6  2-й удар Нефер → лунные бутоны 85% МС; в конце Phantasm Performance ещё
        удар лунных бутонов 120% МС; +15% возвышения лунных бутонов Нефер
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import elemental, occ, lunar_bloom
from ..tags import *

NEFER_NAME = "Нефер"

# --------------------------------------------------------------------------- #
#  Множители                                                                   #
# --------------------------------------------------------------------------- #
SKILL = (1.3749, 2.7498)                 # (АТК, МС)
SKILL_C3 = (1.6232, 3.2463)
PP_NEFER = {1: (0.4435, 0.887), 2: (0.5766, 1.1532)}          # (АТК, МС)
PP_NEFER_C3 = {1: (0.5236, 1.0472), 2: (0.6807, 1.3614)}
PP_SHADES = {1: 1.728, 2: 1.728, 3: 2.304}                   # МС
PP_SHADES_C3 = {1: 2.04, 2: 2.04, 3: 2.72}
C6_SECOND_EM = 0.85                      # C6: 2-й удар Нефер → лунные бутоны
C6_FINAL_EM = 1.20                       # C6: завершающий удар

VEIL_STACKS = 3                          # стаков Veil of Falsehood (всегда 3)
VEIL_STACKS_C2 = 5                       # с C2 — всегда 5
VEIL_PER_STACK = 0.08
A1_EM, C2_EM = 100.0, 200.0
MOONSIGN_PER_EM, MOONSIGN_CAP = 0.000175, 0.14
C1_EM = 0.60
C4_DENDRO_RES = 0.20
C6_ELEVATION = 0.15

SKILLS = 2                               # E × 2
PHANTASMS = 6                            # sCA × 6
NEFER_TIME = 8.5

#: Тег ударов Phantasm Performance (для C1)
PHANTASM = "phantasm"


def _nefer_em(ctx) -> float:
    return ctx.stat(NEFER_NAME, "em", frozenset({ON}))


def veil_multiplier(stacks: int = VEIL_STACKS) -> float:
    return 1.0 + VEIL_PER_STACK * stacks


def _c1_bonus(src):
    """C1: +60% МС к множителю удара лунных бутонов Phantasm Performance."""
    return replace(src, mv=src.mv + C1_EM)


NEFER_KIT = Character(
    name=NEFER_NAME,
    element="dendro",
    weapon_type="catalyst",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 344.0,
        S.BASE_EM: 100.0,
        S.CRIT_VALUE: 0.984,
    },
    buffs=(
        Buff(S.BASE_EM, A1_EM if VEIL_STACKS >= 3 else 0.0, target=SELF,
             source="A Wager of Moonlight: 3 стака Veil of Falsehood, +100 МС"),
        Buff(f"{S.LUNAR_BASE_INC}.lunar_bloom",
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_EM * _nefer_em(ctx)),
             target=TEAM,
             source="Dusklit Eaves: +0.0175% базового урона лунных бутонов за 1 МС (макс. 14%)"),
    ),
    multipliers={"veil": lambda stats: veil_multiplier()},
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            # +60% МС к множителю теней (см. _c1_bonus); C6-удары создаются уже с ним
            patches={f"Phantasm — тень, {n}-й удар (LB)": _c1_bonus for n in (1, 2, 3)},
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=(Buff(S.BASE_EM, C2_EM - A1_EM, target=SELF,
                        source="C2 Нефер: 5 стаков Veil, +200 МС вместо +100"),),
            multipliers={"veil": lambda stats: veil_multiplier(VEIL_STACKS_C2)},
        ),
        3: Constellation(
            number=3, name="C3",
            patches={
                "Навык": lambda s: replace(s, mv=SKILL_C3[0], extra_scaling=(("em", SKILL_C3[1]),)),
                "Phantasm — 1-й удар Нефер": lambda s: replace(
                    s, mv=PP_NEFER_C3[1][0], extra_scaling=(("em", PP_NEFER_C3[1][1]),)),
                "Phantasm — 2-й удар Нефер": lambda s: replace(
                    s, mv=PP_NEFER_C3[2][0], extra_scaling=(("em", PP_NEFER_C3[2][1]),)),
                # меняем только базу навыка — бонус C1 сохраняется
                **{f"Phantasm — тень, {n}-й удар (LB)":
                   (lambda s, n=n: replace(s, mv=s.mv - PP_SHADES[n] + PP_SHADES_C3[n])) # type: ignore
                   for n in (1, 2, 3)},
            },
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(Buff("res_reduction.dendro", C4_DENDRO_RES, target=TEAM,
                        source="C4 Нефер: −20% дендро сопротивления"),),
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(Buff("elevation.lunar_bloom", C6_ELEVATION, target=SELF,
                        source="C6 Нефер: +15% возвышения лунных бутонов"),),
        ),
    },
    note="ДД лунных бутонов (Moonsign).",
)

#: Окна отряда: все удары — под Сахарозой и Инструктором (INST);
#: 18 ударов теней тратят Pale Hymn Лаумы.
_TAGS = (ON, INST)
_SHADE_TAGS = (ON, INST, PALE_HYMN)


def _shade(n: int):
    return lunar_bloom(f"Phantasm — тень, {n}-й удар (LB)", "em", PP_SHADES[n],
                       [occ(PHANTASMS, *_SHADE_TAGS)], kind="charged",
                       extra_tags=(PHANTASM,), multipliers=("veil",))


NEFER_COMBO_DICT = {
    "lb_combo": with_rotation(
        NEFER_KIT,
        sources=(
            elemental("Навык", "atk", SKILL[0], "dendro", "skill", [occ(SKILLS, *_TAGS)],
                      extra_scaling=(("em", SKILL[1]),)),
            elemental("Phantasm — 1-й удар Нефер", "atk", PP_NEFER[1][0], "dendro", "charged",
                      [occ(PHANTASMS, *_TAGS)], extra_scaling=(("em", PP_NEFER[1][1]),),
                      extra_tags=(PHANTASM,), multipliers=("veil",)),
            elemental("Phantasm — 2-й удар Нефер", "atk", PP_NEFER[2][0], "dendro", "charged",
                      [occ(PHANTASMS, *_TAGS)], extra_scaling=(("em", PP_NEFER[2][1]),),
                      extra_tags=(PHANTASM,), multipliers=("veil",)),
            _shade(1), _shade(2), _shade(3),
        ),
        constellation_patches={
            # 2-й удар Нефер становится лунными бутонами (см. C6-источник ниже)
            6: {"Phantasm — 2-й удар Нефер": lambda s: replace(s, occurrences=[])},
        },
        constellation_sources={
            # Pale Hymn на эти удары не тратится (18 стаков уже ушли на тени).
            # Это тоже лунные бутоны Phantasm Performance — C6 включает C1, поэтому
            # множитель сразу с +60% МС.
            6: (
                lunar_bloom("C6: 2-й удар Нефер (LB)", "em", C6_SECOND_EM + C1_EM,
                            [occ(PHANTASMS, *_TAGS)], kind="charged",
                            extra_tags=(PHANTASM,), multipliers=("veil",)),
                lunar_bloom("C6: завершающий удар (LB)", "em", C6_FINAL_EM + C1_EM,
                            [occ(PHANTASMS, *_TAGS)], kind="charged",
                            extra_tags=(PHANTASM,), multipliers=("veil",)),
            ),
        },
    ),
}

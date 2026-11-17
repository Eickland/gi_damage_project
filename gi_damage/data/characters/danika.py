"""
Даника — электро, двуручник. Саппорт отрядов звёздного проводника,
скейлится от АТК.

База: 350 базовой АТК, 0.6 крит-вэлью, +28.8% АТК (возвышение).

Взрыв стихии (5 ударов)
    * 1-й удар: электро 134.9% + звёздный проводник 79.8%
    * 2–4-й удары: электро 21.3%
    * 5-й удар: электро 156.2% + звёздный проводник 119.6%
    * Горничная-защитница: +10% АТК Даники всему отряду (плоская АТК),
      максимум 400 (бета; было 12.5%, макс. 500).
      C1 усиливает бонус на 100%: 20% АТК, максимум 800 (бета; было +80%).
    * Откат взрыва 18 с (бета; было 15 с), стоимость не изменилась.
Навык
    * электро: 77.3% (применение) + 68.5% × 8
    * звёздный проводник: 122.1% × 5
Пассивки
    1) −30% крио и электро сопротивления цели
    2) +14% базового урона звёздного проводника отряду
    3) +60% АТК себе
C3  Взрыв +3 ур.: 158.92%+93.96% / 25.09% / 184.01%+140.88%;
    бонус АТК 11.8% (макс. 472), с C1 ×2 (бета: 10% × 1.18, как раньше 12.5% → 14.75%).
C5  Навык +3 ур.: применение 90.85%, SC 144.16% (электро удары 80.6% —
    допущение, ×1.178).
C6  Якорь: +15% урона SC отряду (бета; было 20%); Горничная-защитница (саппорт):
    +10% урона SC активному персонажу за каждые 1000 АТК Даники (макс. 40%).
C2  (бета: переработано)
    Всем персонажам — по 10 Звёздных перьев: удары звёздного проводника
    получают доп. базовый урон = 80% АТК Даники. Бафф работает только в
    ударах с тегом DANIKA_C2 — его расставляет tag_stellar_conduct_hits()
    в файлах отрядов.

Допущения (в задании не указано):
  * все баффы постоянные (взрыв покрывает ротацию);
  * бонус АТК от взрыва считается от АТК Даники на поле в момент применения
    и сам себя не учитывает (служебный тег DANIKA_SNAPSHOT);
  * применение навыка и взрыв — на поле, 8 электро ударов и 5 ударов SC
    навыка — вне поля.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов
from typing import Iterable, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Build, Character, Constellation, with_rotation
from ...core.sources import (STELLAR_CONDUCT, Occurrence, elemental, occ,
                             stellar_conduct)
from ...core.stats import S
from ..tags import *

DANIKA_NAME = "Даника"

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
#: Взрыв — 5 ударов: 1-й и 5-й — электро + звёздный проводник, 2–4-й — электро.
#: Множители C0 = данные C3 (ур. 13) / 1.178.
BURST_HIT_ELECTRO_MV = (1.349, 1.562)   # электро часть 1-го и 5-го удара
BURST_SC_MV = (0.798, 1.196)            # SC часть 1-го и 5-го удара
BURST_ELECTRO_MV = 0.213                # 2–4-й удары, электро
SKILL_CAST_MV = 0.773             # электро, применение навыка
SKILL_ELECTRO_MV = 0.685          # электро удары навыка
SKILL_SC_MV = 1.221               # удары звёздного проводника навыка

BURST_ATK_SHARE = 0.10            # +10% АТК Даники отряду (бета; было 12.5%)
BURST_ATK_CAP = 400.0             # (бета; было 500)
C1_FACTOR = 2.00                  # C1: бонус АТК от взрыва ×2 (бета; было ×1.8)
C1_ATK_SHARE = BURST_ATK_SHARE * C1_FACTOR   # 20%
C1_ATK_CAP = BURST_ATK_CAP * C1_FACTOR       # 800

#: Откат взрыва (бета: 15 → 18 с). Ротация отряда с Даникой не должна быть короче.
BURST_CD = 18.0

A1_RES_SHRED = 0.30               # −30% крио и электро сопротивления
A2_SC_BASE_INC = 0.14             # +14% базового урона звёздного проводника
A3_ATK_PCT = 0.20                 # +60% АТК себе

# C3: взрыв +3 уровня
C3_BURST_HIT_ELECTRO_MV = (1.5892, 1.8401)
C3_BURST_SC_MV = (0.9396, 1.4088)
C3_BURST_ELECTRO_MV = 0.2509
#: бета: как и раньше, ×1.18 к C0 (12.5% → 14.75%, 500 → 590)
C3_BURST_ATK_SHARE = 0.118
C3_BURST_ATK_CAP = 472.0
# C5: навык +3 уровня
C5_SKILL_CAST_MV = 0.9085
C5_SKILL_SC_MV = 1.4416
C5_SKILL_ELECTRO_MV = 0.806     # не дан — 68.5% × 1.178 (как остальные множители)
# C6
C6_SC_BONUS = 0.15              # якорь: +15% урона SC отряду (бета; было 20%)
C6_ON_FIELD_PER_1000 = 0.10     # Горничная-защитница: +10% урона SC активному за 1000 АТК
C6_ON_FIELD_CAP = 0.40

C2_ATK_SHARE = 0.80               # доп. базовый урон SC = 80% АТК Даники (бета; было 100%)
C2_ACTIVE_STACKS = 10             # стаков активному персонажу
C2_OTHER_STACKS = 10              # стаков остальным (бета: всем по 10; было 7)



def _snapshot_atk(snapshot_tags: Sequence[str]):
    st = frozenset(tuple(snapshot_tags) + (DANIKA_SNAPSHOT,))
    return lambda ctx: ctx.stat(DANIKA_NAME, "atk", st)


def burst_atk_buffs(snapshot_tags: Sequence[str] = (ON,)):
    """Бонус АТК от взрыва (C0). snapshot_tags — состояние Даники при применении."""
    atk = _snapshot_atk(snapshot_tags)
    return (
        Buff(S.FLAT_ATK, lambda ctx: min(BURST_ATK_CAP, BURST_ATK_SHARE * atk(ctx)),
             target=TEAM, excludes=(DANIKA_SNAPSHOT,),
             source="Взрыв Даники: +10% её АТК отряду (макс. 400)"),
    )


def c1_atk_buffs(snapshot_tags: Sequence[str] = (ON,)):
    """C1: прибавка к бонусу взрыва до 20% АТК (макс. 800) — разница с C0."""
    atk = _snapshot_atk(snapshot_tags)

    def delta(ctx) -> float:
        a = atk(ctx)
        return min(C1_ATK_CAP, C1_ATK_SHARE * a) - min(BURST_ATK_CAP, BURST_ATK_SHARE * a)

    return (
        Buff(S.FLAT_ATK, delta, target=TEAM, excludes=(DANIKA_SNAPSHOT,),
             source="C1 Даники: бонус АТК от взрыва +100% (20% АТК, макс. 800)"),
    )


def c3_atk_buffs(snapshot_tags: Sequence[str] = (ON,)):
    """C3: бонус взрыва 11.8% (макс. 472); с C1 ×2 — разница с C1."""
    atk = _snapshot_atk(snapshot_tags)

    def delta(ctx) -> float:
        a = atk(ctx)
        return (min(C3_BURST_ATK_CAP * C1_FACTOR, C3_BURST_ATK_SHARE * C1_FACTOR * a)
                - min(C1_ATK_CAP, C1_ATK_SHARE * a))

    return (
        Buff(S.FLAT_ATK, delta, target=TEAM, excludes=(DANIKA_SNAPSHOT,),
             source="C3 Даники: бонус АТК взрыва 11.8% (макс. 472), с C1 ×2"),
    )


def c6_buffs(stat_tags: Sequence[str] = (OFF,)):
    st = frozenset(stat_tags)
    return (
        Buff(S.SC_BONUS, C6_SC_BONUS, target=TEAM,
             source="C6 Даники: якорь, +15% урона звёздного проводника отряду"),
        Buff(S.SC_BONUS,
             lambda ctx: min(C6_ON_FIELD_CAP,
                             C6_ON_FIELD_PER_1000 * ctx.stat(DANIKA_NAME, "atk", st) / 1000.0),
             target=OTHERS, requires=(ON,),
             source="C6 Даники: +10% урона SC активному за 1000 её АТК (макс. 40%)"),
    )


def _mv(v):
    return lambda src: replace(src, mv=v)


def c2_buffs(stat_tags: Sequence[str] = (OFF,)):
    """C2: доп. базовый урон ударов SC = 80% АТК Даники (в ударах с DANIKA_C2)."""
    st = frozenset(stat_tags)
    return (
        Buff(f"{S.FLAT_BASE_DMG}.{STELLAR_CONDUCT}",
             lambda ctx: C2_ATK_SHARE * ctx.stat(DANIKA_NAME, "atk", st),
             target=TEAM, requires=(DANIKA_C2,),
             source="C2 Даники: +80% её АТК к базовому урону звёздного проводника"),
    )


DANIKA_KIT = Character(
    name=DANIKA_NAME,
    element="electro",
    weapon_type="claymore",
    default_field=OFF,
    polar_always=2.0,   # стаки Polestar отряду
    crit_mode="balance",
    stats={
        S.BASE_ATK: 337.0,
        S.ATK_PCT: 0.288,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        Buff("res_reduction.cryo", A1_RES_SHRED, target=TEAM,
             source="Пассивка 1 Даники: −30% крио сопротивления"),
        Buff("res_reduction.electro", A1_RES_SHRED, target=TEAM,
             source="Пассивка 1 Даники: −30% электро сопротивления"),
        Buff(S.SC_BASE_INC, A2_SC_BASE_INC, target=TEAM,
             source="Пассивка 2 Даники: +14% базового урона звёздного проводника"),
        Buff(S.ATK_PCT, A3_ATK_PCT, target=SELF,
             source="Пассивка 3 Даники: +60% АТК себе"),
    ),
    sources=(),
    # Баффы взрыва/C1/C2 зависят от ротации (состояние снапшота) — добавляются
    # в danika_rotation().
    constellations={
        1: Constellation(number=1, name="C1"),
        2: Constellation(number=2, name="C2"),
        3: Constellation(number=3, name="C3", patches={
            "Взрыв — электро, 1-й удар": _mv(C3_BURST_HIT_ELECTRO_MV[0]),
            "Взрыв — электро, 5-й удар": _mv(C3_BURST_HIT_ELECTRO_MV[1]),
            "Взрыв — звёздный проводник, 1-й удар": _mv(C3_BURST_SC_MV[0]),
            "Взрыв — звёздный проводник, 5-й удар": _mv(C3_BURST_SC_MV[1]),
            "Взрыв — электро удары": _mv(C3_BURST_ELECTRO_MV),
        }),
        5: Constellation(number=5, name="C5", patches={
            "Навык — применение": _mv(C5_SKILL_CAST_MV),
            "Навык — электро удары": _mv(C5_SKILL_ELECTRO_MV),
            "Навык — звёздный проводник": _mv(C5_SKILL_SC_MV),
        }),
    },
    note="Саппорт звёздного проводника.",
)


def _danika_combo(sources, snapshot_tags=(ON,), c2_stat_tags=(OFF,)) -> Character:
    """Комбо Даники: удары + баффы, которые снимают АТК в заданном состоянии.

    snapshot_tags — состояние Даники при применении взрыва (бонус АТК);
    c2_stat_tags  — состояние, в котором берётся АТК для C2.
    """
    return with_rotation(
        DANIKA_KIT,
        sources=sources,
        extra_buffs=burst_atk_buffs(tuple(snapshot_tags)),
        constellation_extra_buffs={
            1: c1_atk_buffs(tuple(snapshot_tags)),
            2: c2_buffs(tuple(c2_stat_tags)),
            3: c3_atk_buffs(tuple(snapshot_tags)),
            6: c6_buffs(tuple(c2_stat_tags)),
        },
    )


#: Каждая строка occ(N, теги...) — N ударов в этом наборе окон; одинаковые
#: удары с разными баффами идут строками подряд.
DANIKA_COMBO_DICT = {
    # Даника первой в ротации: E Q, дальше уходит с поля.
    "support_eq": _danika_combo((
        elemental("Навык — применение", "atk", SKILL_CAST_MV, "electro", "skill", [
            occ(1, ON),
        ]),
        elemental("Навык — электро удары", "atk", SKILL_ELECTRO_MV, "electro", "skill", [
            occ(8, OFF),
        ]),
        stellar_conduct("Навык — звёздный проводник", "atk", SKILL_SC_MV, "electro", [
            occ(1, OFF),
        ], kind="skill"),
        elemental("Взрыв — электро, 1-й удар", "atk", BURST_HIT_ELECTRO_MV[0], "electro", "burst", [
            occ(1, ON),
        ]),
        stellar_conduct("Взрыв — звёздный проводник, 1-й удар", "atk", BURST_SC_MV[0], "electro", [
            occ(1, ON),
        ], kind="burst"),
        elemental("Взрыв — электро, 5-й удар", "atk", BURST_HIT_ELECTRO_MV[1], "electro", "burst", [
            occ(1, ON),
        ]),
        stellar_conduct("Взрыв — звёздный проводник, 5-й удар", "atk", BURST_SC_MV[1], "electro", [
            occ(1, ON),
        ], kind="burst"),
        elemental("Взрыв — электро удары", "atk", BURST_ELECTRO_MV, "electro", "burst", [
            occ(3, ON),
        ]),
    ), snapshot_tags=(ON,), c2_stat_tags=(OFF,)),
    # После Алеши (Знать 4ч): все удары и снапшот АТК — в окне NOBLE.
    "support_eq_noble": _danika_combo((
        elemental("Навык — применение", "atk", SKILL_CAST_MV, "electro", "skill", [
            occ(1, ON, NOBLE),
        ]),
        elemental("Навык — электро удары", "atk", SKILL_ELECTRO_MV, "electro", "skill", [
            occ(8, OFF, NOBLE),
        ]),
        stellar_conduct("Навык — звёздный проводник", "atk", SKILL_SC_MV, "electro", [
            occ(1, OFF, NOBLE),
        ], kind="skill"),
        elemental("Взрыв — электро, 1-й удар", "atk", BURST_HIT_ELECTRO_MV[0], "electro", "burst", [
            occ(1, ON, NOBLE),
        ]),
        stellar_conduct("Взрыв — звёздный проводник, 1-й удар", "atk", BURST_SC_MV[0], "electro", [
            occ(1, ON, NOBLE),
        ], kind="burst"),
        elemental("Взрыв — электро, 5-й удар", "atk", BURST_HIT_ELECTRO_MV[1], "electro", "burst", [
            occ(1, ON, NOBLE),
        ]),
        stellar_conduct("Взрыв — звёздный проводник, 5-й удар", "atk", BURST_SC_MV[1], "electro", [
            occ(1, ON, NOBLE),
        ], kind="burst"),
        elemental("Взрыв — электро удары", "atk", BURST_ELECTRO_MV, "electro", "burst", [
            occ(3, ON, NOBLE),
        ]),
    ), snapshot_tags=(ON, NOBLE), c2_stat_tags=(OFF, NOBLE)),
}


# --------------------------------------------------------------------------- #
#  Расстановка тегов по ударам (стаки C2 Даники и т.п.)                         #
# --------------------------------------------------------------------------- #
def tag_stellar_conduct_hits(build: Build, tag: str, hits: float) -> Build:
    """Пометить тегом `tag` первые `hits` ударов звёздного проводника сборки.

    «Первые» = из вхождений с наибольшим числом тегов состояния (в них
    собрано больше всего окон усилений, то есть это начало ротации после
    саппортов); при равенстве — в порядке источников. Вхождение, которое
    помечается не целиком, делится на две части.

    Работает по итоговым источникам с учётом созвездий, результат кладётся
    в extra_sources — поэтому вызывайте ПОСЛЕ выбора созвездия (в build-функции),
    а не через Variation(constellations=...).
    """
    if hits <= 0:
        return build
    sources = build.all_sources()
    cands = [(i, j) for i, s in enumerate(sources) if s.model == STELLAR_CONDUCT
             for j in range(len(s.occurrences))]
    cands.sort(key=lambda ij: -len(sources[ij[0]].occurrences[ij[1]].state))
    take = {}
    left = float(hits)
    for i, j in cands:
        if left <= 1e-9:
            break
        n = min(float(sources[i].occurrences[j].count), left)
        take[(i, j)] = n
        left -= n
    patched = []
    for i, s in enumerate(sources):
        new_occ = []
        for j, o in enumerate(s.occurrences):
            n = take.get((i, j), 0.0)
            if n > 1e-9:
                new_occ.append(Occurrence(frozenset(o.state | {tag}), n))
            if o.count - n > 1e-9:
                new_occ.append(Occurrence(o.state, o.count - n))
        patched.append(replace(s, occurrences=new_occ))
    return replace(build, extra_sources=tuple(patched))


def add_tags(build: Build, *tags: str) -> Build:
    """Добавить теги ко всем ударам сборки (весь кусок ротации в одном окне)."""
    sources = build.all_sources()
    patched = [replace(s, occurrences=[Occurrence(frozenset(o.state | set(tags)), o.count)
                                       for o in s.occurrences]) for s in sources]
    return replace(build, extra_sources=tuple(patched))

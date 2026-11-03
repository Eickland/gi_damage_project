"""
Даника — электро, двуручник. Саппорт отрядов звёздного проводника,
скейлится от АТК.

База: 350 базовой АТК, 0.6 крит-вэлью, +28.8% АТК (возвышение).

Взрыв стихии
    * 2 удара звёздного проводника: 134.6% и 155.9% АТК
    * 3 электро удара по 21.3% АТК
    * +12.5% АТК Даники всему отряду (плоская АТК), максимум 500.
      C1 усиливает бонус на 80%: 22.5% АТК, максимум 900.
Навык
    * электро: 77.3% (применение) + 68.5% × 8
    * звёздный проводник: 122.1% × 5
Пассивки
    1) −30% крио и электро сопротивления цели
    2) +14% базового урона звёздного проводника отряду
    3) +60% АТК себе
C2
    Удары звёздного проводника получают доп. базовый урон = 100% АТК Даники.
    Стаков: 10 активному персонажу, 7 остальным. Бафф работает только в
    ударах с тегом DANIKA_C2 — его расставляет tag_stellar_conduct_hits()
    в файлах отрядов.

Допущения (в задании не указано):
  * все баффы постоянные (взрыв покрывает ротацию);
  * бонус АТК от взрыва считается от АТК Даники на поле в момент применения
    и сам себя не учитывает (служебный тег DANIKA_SNAPSHOT);
  * стаки «полярности» у ударов звёздного проводника Даники — DANIKA_POLAR_STACKS;
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
BURST_SC_MV = (1.346, 1.559)      # 2 удара звёздного проводника
BURST_ELECTRO_MV = 0.213          # электро удары взрыва
BURST_ELECTRO_HITS = 3
SKILL_CAST_MV = 0.773             # электро, применение навыка
SKILL_ELECTRO_MV = 0.685          # электро удары навыка
SKILL_ELECTRO_HITS = 8
SKILL_SC_MV = 1.221               # удары звёздного проводника навыка
SKILL_SC_HITS = 5

BURST_ATK_SHARE = 0.125           # +12.5% АТК Даники отряду
BURST_ATK_CAP = 500.0
C1_FACTOR = 1.80                  # C1: бонус АТК от взрыва ×1.8
C1_ATK_SHARE = BURST_ATK_SHARE * C1_FACTOR   # 22.5%
C1_ATK_CAP = 900.0

A1_RES_SHRED = 0.30               # −30% крио и электро сопротивления
A2_SC_BASE_INC = 0.14             # +14% базового урона звёздного проводника
A3_ATK_PCT = 0.60                 # +60% АТК себе

C2_ATK_SHARE = 1.00               # доп. базовый урон SC = 100% АТК Даники
C2_ACTIVE_STACKS = 10             # стаков активному персонажу
C2_OTHER_STACKS = 7               # стаков остальным

#: Стаки «полярности» для звёздного проводника Даники
DANIKA_POLAR_STACKS = 7


def _snapshot_atk(snapshot_tags: Sequence[str]):
    st = frozenset(tuple(snapshot_tags) + (DANIKA_SNAPSHOT,))
    return lambda ctx: ctx.stat(DANIKA_NAME, "atk", st)


def burst_atk_buffs(snapshot_tags: Sequence[str] = (ON,)):
    """Бонус АТК от взрыва (C0). snapshot_tags — состояние Даники при применении."""
    atk = _snapshot_atk(snapshot_tags)
    return (
        Buff(S.FLAT_ATK, lambda ctx: min(BURST_ATK_CAP, BURST_ATK_SHARE * atk(ctx)),
             target=TEAM, excludes=(DANIKA_SNAPSHOT,),
             source="Взрыв Даники: +12.5% её АТК отряду (макс. 500)"),
    )


def c1_atk_buffs(snapshot_tags: Sequence[str] = (ON,)):
    """C1: прибавка к бонусу взрыва до 22.5% АТК (макс. 900) — разница с C0."""
    atk = _snapshot_atk(snapshot_tags)

    def delta(ctx) -> float:
        a = atk(ctx)
        return min(C1_ATK_CAP, C1_ATK_SHARE * a) - min(BURST_ATK_CAP, BURST_ATK_SHARE * a)

    return (
        Buff(S.FLAT_ATK, delta, target=TEAM, excludes=(DANIKA_SNAPSHOT,),
             source="C1 Даники: бонус АТК от взрыва +80% (22.5% АТК, макс. 900)"),
    )


def c2_buffs(stat_tags: Sequence[str] = (OFF,)):
    """C2: доп. базовый урон ударов SC = 100% АТК Даники (в ударах с DANIKA_C2)."""
    st = frozenset(stat_tags)
    return (
        Buff(f"{S.FLAT_BASE_DMG}.{STELLAR_CONDUCT}",
             lambda ctx: C2_ATK_SHARE * ctx.stat(DANIKA_NAME, "atk", st),
             target=TEAM, requires=(DANIKA_C2,),
             source="C2 Даники: +100% её АТК к базовому урону звёздного проводника"),
    )


DANIKA_KIT = Character(
    name=DANIKA_NAME,
    element="electro",
    weapon_type="claymore",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 350.0,
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
    },
    note="Саппорт звёздного проводника.",
)


def danika_rotation(on_tags: Sequence[str] = (ON,), off_tags: Sequence[str] = (OFF,),
                    snapshot_tags: Sequence[str] | None = None,
                    c2_stat_tags: Sequence[str] | None = None,
                    polar_stacks: int = DANIKA_POLAR_STACKS) -> Character:
    """Даника под конкретную ротацию: E Q.

    on_tags       — теги ударов на поле (применение навыка, взрыв);
    off_tags      — теги ударов вне поля (электро и SC удары навыка);
    snapshot_tags — состояние, в котором берётся АТК для бонуса взрыва
                    (по умолчанию = on_tags);
    c2_stat_tags  — состояние, в котором берётся АТК для C2 (по умолчанию = off_tags).
    """
    on_tags, off_tags = tuple(on_tags), tuple(off_tags)
    snapshot_tags = tuple(snapshot_tags) if snapshot_tags is not None else on_tags
    c2_stat_tags = tuple(c2_stat_tags) if c2_stat_tags is not None else off_tags
    return with_rotation(
        DANIKA_KIT,
        sources=(
            elemental("Навык — применение", "atk", SKILL_CAST_MV, "electro", "skill",
                      [occ(1, *on_tags)]),
            elemental("Навык — электро удары", "atk", SKILL_ELECTRO_MV, "electro", "skill",
                      [occ(SKILL_ELECTRO_HITS, *off_tags)]),
            stellar_conduct("Навык — звёздный проводник", "atk", SKILL_SC_MV, "electro",
                            [occ(SKILL_SC_HITS, *off_tags)], kind="skill",
                            polar_stacks=polar_stacks),
            stellar_conduct("Взрыв — звёздный проводник, 1-й удар", "atk", BURST_SC_MV[0],
                            "electro", [occ(1, *on_tags)], kind="burst",
                            polar_stacks=polar_stacks),
            stellar_conduct("Взрыв — звёздный проводник, 2-й удар", "atk", BURST_SC_MV[1],
                            "electro", [occ(1, *on_tags)], kind="burst",
                            polar_stacks=polar_stacks),
            elemental("Взрыв — электро удары", "atk", BURST_ELECTRO_MV, "electro", "burst",
                      [occ(BURST_ELECTRO_HITS, *on_tags)]),
        ),
        extra_buffs=burst_atk_buffs(snapshot_tags),
        constellation_extra_buffs={
            1: c1_atk_buffs(snapshot_tags),
            2: c2_buffs(c2_stat_tags),
        },
    )


DANIKA_COMBO_DICT = {
    # Даника первой в ротации: E Q, дальше уходит с поля.
    "support_eq": danika_rotation(),
    # После Алеши (Знать 4ч): все удары и снапшот АТК — в окне NOBLE.
    "support_eq_noble": danika_rotation(on_tags=(ON, NOBLE), off_tags=(OFF, NOBLE)),
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

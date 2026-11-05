"""
Отряд звёздного проводника: Сандроне / Одетта / C6 Алеша / Даника.

Ротация: Алеша EQ / Даника EQ / Одетта EE / Сандроне E CA EQ CA E CA E.
Реакций, наносящих урон, нет. Резонанс — крио (2 крио + 2 электро).

Артефакты: Даника — Сердце горна, Алеша — Знать, остальные — Разочарование.
Знать (окно NOBLE): у Сандроне окно уже размечено в её комбо; Даника и
Одетта идут сразу после взрыва Алеши — все их удары считаются в окне.

C2 Даники: стаки доп. базового урона SC расставлены по ударам —
Сандроне (активная) 10, Одетта 7, сама Даника 7
(см. danika.tag_stellar_conduct_hits). У Алеши ударов SC нет.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.sandrone import SANDRONE_COMBO_DICT
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits,
                                       add_tags)
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Алеша": 1.9, "Даника": 1.9, "Одетта": 2.4}

ROTATION = "Алеша EQ/Даника EQ/Одетта EE/Сандроне E CA EQ CA E CA E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def sandrone_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(DISENCHANTMENT,),
                   main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                   extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=SANDRONE_COMBO_DICT["sandrone_sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    ), danika_c2_hits)


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(DISENCHANTMENT,),
                 use_burst: bool | None = None, danika_c2_hits: int = 0,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return _c2(add_tags(Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    ), NOBLE), danika_c2_hits)


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(NOBLESSE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ALYOSHA_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(HEART_OF_FORGE,),
                 main_stats=FULL_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=DANIKA_COMBO_DICT["support_eq_noble"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    ), C2_OTHER_STACKS if constellation >= 2 else 0)


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=TEASPOON,
              odette_c: int = 2, odette_weapon=SILVER_LIGHT,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              danika_c: int = 0, danika_weapon=ATONEMENT,
              sandrone_artifacts=(DISENCHANTMENT,), odette_artifacts=(STELLAR_SET,),
              alyosha_artifacts=(NOBLESSE,), danika_artifacts=(HEART_OF_FORGE,)) -> Team:
    c2 = danika_c >= 2
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts,
                           danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            odette_build(odette_c, odette_weapon, odette_artifacts,
                         danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
            danika_build(danika_c, danika_weapon, danika_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(sandrone_c: int = 0, sandrone_weapon=ATONEMENT, odette_c: int = 0,
              odette_weapon=SILVER_LIGHT, alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              danika_c: int = 2, danika_weapon=ATONEMENT) -> str:
    _dw = (f" ({danika_weapon.name})" if danika_weapon.name != ATONEMENT.name else "")
    return (f"C{sandrone_c}R{sandrone_weapon.refinement} Сандроне, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта, "
            f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша, "
            f"C{danika_c}R{danika_weapon.refinement} Даника{_dw}")


#: Вариации: C0 / C1 / C2 Даники
VARIANTS = (
    {"danika_c": 0},
    {"danika_c": 1},
    {"danika_c": 2},
            {"danika_c": 0, "danika_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out

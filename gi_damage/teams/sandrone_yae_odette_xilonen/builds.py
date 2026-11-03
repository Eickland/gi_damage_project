"""
Отряд звёздного проводника: Сандроне / Яэ Мико / Одетта / Шилонен.

Ротация: Одетта EE / Яэ EEE / Шилонен E / Сандроне E CA EQ CA /
         Шилонен E / Сандроне E CA E.
Реакций, наносящих урон, нет.

Отряду (постоянно):
    Крио резонанс (Сандроне + Одетта): +15% крит. шанса;
    Шилонен: −36% сопротивления к электро / крио / пиро / гидро / гео (C3: −45%).

Окна баффов:
    INST (Инструктор на Шилонен, +120 МС) — те же удары Сандроне и Одетты,
         что были под A4 Сахарозы в её комбо (sandrone_sc_sucrose_combo,
         odette_ssc_combo_sucrose_sandrone); у Яэ — 4 из 7 усиленных молний.
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
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.xilonen import XILONEN_COMBO_DICT, XILONEN_TIME
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Одетта": 2.4, "Яэ Мико": 2.4, "Шилонен": XILONEN_TIME}

ROTATION = ("Одетта EE/Яэ EEE/Шилонен E/Сандроне E CA EQ CA/"
            "Шилонен E/Сандроне E CA E")


def enemy() -> Enemy:
    return Enemy(res={"cryo": 0.10, "electro": 0.10, "geo": 0.10},
                 def_mult=0.4875, elevation=0.0)


def sandrone_build(constellation: int = 0, weapon=TIDAL_SHADOW, artifacts=(DISENCHANTMENT,),
                   main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
                   extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SANDRONE_COMBO_DICT["sandrone_sc_sucrose_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(HEART_OF_FORGE,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo_sucrose_sandrone"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (tuple(odette_burst_buffs(constellation))
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
              main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE_COMBO_DICT["yae_sc_instructor_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )


def xilonen_build(constellation: int = 0, weapon=FAV_SWORD, artifacts=(INSTRUCTOR,),
                  main_stats={S.DEF_PCT: 0.583 * 2, S.CRIT_VALUE: 0.622},
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=XILONEN_COMBO_DICT["ee"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Шилонен"],
    )


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=TIDAL_SHADOW,
              yae_c: int = 2, yae_weapon=ECHOES.at(5),
              odette_c: int = 2, odette_weapon=SILVER_LIGHT,
              xilonen_c: int = 2, xilonen_weapon=FAV_SWORD,
              sandrone_artifacts=(DISENCHANTMENT,), yae_artifacts=(HEART_OF_FORGE,),
              odette_artifacts=(DISENCHANTMENT,), xilonen_artifacts=(INSTRUCTOR,)) -> Team:
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            xilonen_build(xilonen_c, xilonen_weapon, xilonen_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(sandrone_c=0, yae_c=1, odette_c=0, xilonen_c=0) -> str:
    return (f"C{sandrone_c}R0 Сандроне, C{yae_c}R5 Яэ, C{odette_c}R0 Одетта, "
            f"C{xilonen_c}R0 Шилонен")


BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}

"""
Отряд звёздного проводника: Сандроне / Яэ Мико / Алеша / Одетта.

Реакций, наносящих урон, нет.
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
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Алеша": 1.65, "Одетта": 2.4, "Яэ Мико": 2.4}

ROTATION = "Алеша EQ/Одетта EE/Яэ EEE/Сандроне E CA EQ CA E CA E"


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def sandrone_build(constellation: int = 0, weapon=TIDAL_SHADOW, artifacts=(DISENCHANTMENT,),
                   main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
                   extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SANDRONE_COMBO_DICT["sandrone_sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(MILLELITH,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
              main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE_COMBO_DICT["sc_eee"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
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


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=THOUSAND_SUNS,
              odette_c: int = 2, odette_weapon=FROSTFEATHER,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              sandrone_artifacts=(DISENCHANTMENT,), odette_artifacts=(DISENCHANTMENT,),
              yae_artifacts=(MILLELITH,), alyosha_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


BASE_NAME = "C0R0 Сандроне, C1R5 Яэ, С6R0 Алеша, C0R0 Одетта"


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}

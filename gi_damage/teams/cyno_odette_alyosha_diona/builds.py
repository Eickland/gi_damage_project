"""
Отряд звёздного проводника: Сайно / Одетта / Алеша / Диона.

Реакций, наносящих урон, нет (звёздный проводник).
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
from ...data.characters.cyno import CYNO_COMBO_DICT
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.characters.diona import DIONA_COMBO_DICT
from ...data.weapons import *



#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сайно": 15.0, "Алеша": 1.65, "Одетта": 2.4, "Диона": 2.2}

ROTATION = "Алеша EQ/Одетта EE/Диона EQ/Сайно QE (N2 CA N4 E)×3"

#: Главные статы Сайно: пески/кубок/корона (по умолчанию МС/АТК/крит — лучший из трёх)
CYNO_MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}          # АТК/АТК/крит
CYNO_MAIN_EM = {S.BASE_EM: 187.0, S.ATK_PCT: 0.466, S.CRIT_VALUE: 0.622}  # МС/АТК/крит
CYNO_MAIN_ELECTRO = {S.ATK_PCT: 0.466, "dmg_bonus.electro": 0.466,
                     S.CRIT_VALUE: 0.622}                             # АТК/электро/крит


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def cyno_build(constellation: int = 1, weapon=DEATHMATCH, artifacts=(DISENCHANTMENT,),
               main_stats=CYNO_MAIN_EM, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CYNO_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сайно"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(MILLELITH,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo_sucrose"],
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


def alyosha_build(constellation: int = 2, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
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


def diona_build(constellation: int = 6, weapon=FAV_BOW.at(5), artifacts=(NOBLESSE,),
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=DIONA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Диона"],
    )


def make_team(name: str, cyno_c: int = 1, cyno_weapon=DEATHMATCH,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              cyno_artifacts=(DISENCHANTMENT,), odette_artifacts=(MILLELITH,),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE, alyosha_artifacts=(HEART_OF_FORGE,),
              diona_c: int = 6, diona_weapon=FAV_BOW.at(5), diona_artifacts=(NOBLESSE,),
              cyno_main_stats=CYNO_MAIN_EM) -> Team:
    return Team(
        name=name,
        builds=[
            cyno_build(cyno_c, cyno_weapon, cyno_artifacts, cyno_main_stats),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
            diona_build(diona_c, diona_weapon, diona_artifacts),
        ],
        enemy=enemy(),
        rotation=ROTATION,
        config=Config(),
    )


BASE_NAME = "C1R1 Сайно, C0R0 Одетта, С6R0 Алеша, С6R0 Диона"


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}

"""
Отряд звёздного проводника: Сайно / Одетта / Яэ Мико / Алеша.

Реакций, наносящих урон, нет (звёздный проводник). Резонанс — электро
(без бонуса урона), поэтому отрядных баффов нет.
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
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS: tuple = ()

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сайно": 15.0, "Алеша": 1.65, "Одетта": 2.4, "Яэ Мико": 2.4}

ROTATION = "Одетта EE/Яэ EEE/Алеша EQ/Сайно QE (N2 CA N4 E)×3"

#: Главные статы: пески/кубок/корона
MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}                    # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0*2, S.CRIT_VALUE: 0.622}       # МС/АТК/крит
MAIN_ELECTRO = {S.ATK_PCT: 0.466, "dmg_bonus.electro": 0.466,
                S.CRIT_VALUE: 0.622}                                      # АТК/электро/крит

CYNO_MAIN = MAIN_EM
YAE_MAIN = MAIN_ATK


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def cyno_build(constellation: int = 1, weapon=DEATHMATCH, artifacts=(DISENCHANTMENT,),
               main_stats=CYNO_MAIN, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CYNO_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сайно"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(HEART_OF_FORGE,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo_cyno"],
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


def yae_build(constellation: int = 1, weapon=ECHOES.at(5),
              artifacts=(DISENCHANTMENT,), main_stats=YAE_MAIN,
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


def make_team(name: str, cyno_c: int = 2, cyno_weapon=SCARLET_SANDS.at(2),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              yae_c: int = 2, yae_weapon=KAGURA,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              cyno_artifacts=(DISENCHANTMENT,), odette_artifacts=(HEART_OF_FORGE,),
              yae_artifacts=(DISENCHANTMENT,), alyosha_artifacts=(NOBLESSE,),
              cyno_main_stats=CYNO_MAIN, yae_main_stats=YAE_MAIN) -> Team:
    return Team(
        name=name,
        builds=[
            cyno_build(cyno_c, cyno_weapon, cyno_artifacts, cyno_main_stats),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts, yae_main_stats),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


BASE_NAME = "C2R2 Сайно, C0R0 Одетта, C2R1 Яэ, С6R0 Алеша"


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
